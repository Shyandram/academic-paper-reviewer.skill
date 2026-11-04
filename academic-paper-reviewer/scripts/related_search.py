#!/usr/bin/env python3
"""Search for related work online without ever surfacing the reviewed paper.

The reviewed paper is described by a *fingerprint* (title, method names,
authors, identifiers, URLs, distinctive phrases, cutoff date). Every query is
checked against it before it is sent, and every result is filtered against it
before anyone reads it. All decisions go to a JSON-lines ledger for audit.

Subcommands (standard library only):

  fingerprint  --paper paper.txt --out fp.json
      Draft a fingerprint: extracts arXiv IDs, code/project URLs and a title
      guess. Edit the file to fix the title and add method names, authors,
      distinctive phrases and the cutoff date before searching.

  search       --fp fp.json --query "concept words" [--max 25] [--mode on|strict]
      Query the arXiv API, filter the results, print kept results as JSON.

  filter       --fp fp.json --results hits.json [--mode on|strict]
      Filter results from another search tool (a JSON list of objects with
      title, url, snippet/abstract, date, authors).

  verify       --fp fp.json --title "Recommended reference title"
      Check that a recommended reference exists on arXiv (title match).

Common option: --ledger search_ledger.jsonl (default: next to the fingerprint).

Filtering rules (see references/literature_search.md):
  drop  self-match: title similarity >= 0.8, a method name in title/abstract,
        a matching arXiv ID or URL, a distinctive phrase in the abstract, or
        >= 2 shared authors within 183 days of the cutoff
  drop  outcome-revealing pages: OpenReview forums, accepted-paper and award lists
  drop  post-cutoff results in strict mode; in "on" mode they are kept but
        labelled "newer" (never a required comparison)
  keep  everything else, classified as prior / concurrent (<= 60 days before
        the cutoff) / newer
"""

import argparse
import datetime as dt
import difflib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ARXIV_API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom"}
TITLE_SIM = 0.8
AUTHOR_WINDOW_DAYS = 183
CONCURRENT_DAYS = 60
STOP = {"a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "into",
        "is", "it", "of", "on", "or", "the", "to", "via", "with", "without", "towards",
        "using", "we", "our", "this", "that", "based"}
BLOCKED = [
    (r"openreview\.net/(forum|pdf|notes|attachment)", "OpenReview page (may reveal reviews or the decision)"),
    (r"openreview\.net/group\?id=.*(accept|decision|oral|poster|spotlight)", "OpenReview decision list"),
    (r"/(accepted[-_ ]?papers|acceptedpapers|awards?|paper[-_ ]?awards)\b", "accepted-paper or award list"),
    (r"(papercopilot|paperdigest)\.", "acceptance/statistics aggregator"),
    (r"/Conferences/\d{4}/(AcceptedPapers|Awards|Orals|Highlights)", "venue acceptance list"),
]


# ---------------------------------------------------------------- utilities

def norm(text):
    text = re.sub(r"-\s*\n\s*", "", str(text or ""))
    return re.sub(r"\s+", " ", re.sub(r"[^0-9a-z]+", " ", text.lower())).strip()


def tokens(text):
    return [t for t in norm(text).split() if t not in STOP and len(t) > 1]


def parse_date(value):
    if not value:
        return None
    m = re.search(r"(\d{4})-(\d{2})(?:-(\d{2}))?", str(value))
    if not m:
        m2 = re.search(r"\b(19|20)\d{2}\b", str(value))
        return dt.date(int(m2.group(0)), 7, 1) if m2 else None
    return dt.date(int(m.group(1)), int(m.group(2)), int(m.group(3) or 1))


def arxiv_base(identifier):
    m = re.search(r"(\d{4}\.\d{4,5})(v\d+)?", str(identifier or ""))
    return m.group(1) if m else None


def surname(name):
    parts = norm(name).split()
    return parts[-1] if parts else ""


def load_fp(path):
    fp = json.loads(Path(path).read_text())
    fp.setdefault("method_names", [])
    fp.setdefault("authors", [])
    fp.setdefault("arxiv_ids", [])
    fp.setdefault("urls", [])
    fp.setdefault("distinctive_phrases", [])
    if not fp.get("title"):
        sys.exit("error: fingerprint has no title; edit the fingerprint file first")
    if not fp.get("cutoff_date"):
        sys.exit("error: fingerprint has no cutoff_date (YYYY-MM-DD); edit the fingerprint file first")
    return fp


def ledger_write(path, record):
    record = {"time": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), **record}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- guards

def check_query(query, fp):
    """Return a reason string if the query could retrieve the paper itself."""
    q = norm(query)
    for name in fp["method_names"]:
        if name and re.search(rf"\b{re.escape(norm(name))}\b", q):
            return f"query contains the method name '{name}'"
    for a in fp["authors"]:
        s = surname(a)
        if len(s) > 2 and re.search(rf"\b{re.escape(s)}\b", q):
            return f"query contains author surname '{s}'"
    for ident in fp["arxiv_ids"]:
        if arxiv_base(ident) and arxiv_base(ident) in query:
            return "query contains the paper's arXiv ID"
    title_toks = set(tokens(fp["title"]))
    q_toks = set(tokens(query))
    if title_toks and len(q_toks & title_toks) / len(title_toks) >= 0.6:
        return "query reproduces most of the paper's title"
    return None


def self_match(hit, fp):
    """Return a reason string if the hit is (or reveals) the reviewed paper."""
    title, abstract = hit.get("title", ""), hit.get("abstract") or hit.get("snippet") or ""
    url = hit.get("url", "") or ""
    if difflib.SequenceMatcher(None, norm(title), norm(fp["title"])).ratio() >= TITLE_SIM:
        return "title matches the reviewed paper"
    text = norm(title + " " + abstract)
    for name in fp["method_names"]:
        if name and re.search(rf"\b{re.escape(norm(name))}\b", text):
            return f"mentions the method name '{name}'"
    ids = {arxiv_base(i) for i in fp["arxiv_ids"]} - {None}
    if arxiv_base(hit.get("id", "")) in ids or arxiv_base(url) in ids:
        return "same arXiv ID"
    for u in fp["urls"]:
        core = re.sub(r"^https?://(www\.)?", "", u.rstrip("/").lower())
        if core and core in url.lower():
            return "URL matches the paper's code or project page"
    for phrase in fp["distinctive_phrases"]:
        p = norm(phrase)
        if len(p.split()) >= 5 and p in norm(abstract):
            return "abstract contains a distinctive phrase of the reviewed paper"
    shared = {surname(a) for a in fp["authors"]} & {surname(a) for a in hit.get("authors", [])}
    shared.discard("")
    if len(shared) >= 2:
        d, cutoff = parse_date(hit.get("date")), parse_date(fp["cutoff_date"])
        if d is None or abs((d - cutoff).days) <= AUTHOR_WINDOW_DAYS:
            return f"{len(shared)} shared authors close to the cutoff date"
    return None


def blocked(hit):
    url = hit.get("url", "") or ""
    for pattern, reason in BLOCKED:
        if re.search(pattern, url, re.I):
            return reason
    return None


def classify(hit, fp, mode):
    """Return (keep, label_or_reason)."""
    reason = self_match(hit, fp) or blocked(hit)
    if reason:
        return False, reason
    d, cutoff = parse_date(hit.get("date")), parse_date(fp["cutoff_date"])
    if d is None:
        return True, "undated (treat as concurrent at most)"
    if d > cutoff:
        if mode == "strict":
            return False, "published after the cutoff date (strict mode)"
        return True, "newer (after the cutoff; never a required comparison)"
    if (cutoff - d).days <= CONCURRENT_DAYS:
        return True, "concurrent (within 60 days before the cutoff; discuss, don't require)"
    return True, "prior"


def filter_hits(hits, fp, mode, ledger, source):
    kept = []
    for h in hits:
        keep, label = classify(h, fp, mode)
        entry = {"title": h.get("title"), "date": h.get("date"), "url": h.get("url")}
        ledger_write(ledger, {"event": "keep" if keep else "drop", "source": source,
                              "reason": label, **entry})
        if keep:
            kept.append({**entry, "authors": h.get("authors", [])[:6], "label": label,
                         "abstract": (h.get("abstract") or h.get("snippet") or "")[:600]})
    return kept


# ---------------------------------------------------------------- arXiv

def arxiv_query(search_query, max_results):
    url = ARXIV_API + "?" + urllib.parse.urlencode(
        {"search_query": search_query, "max_results": max_results,
         "sortBy": "relevance", "sortOrder": "descending"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                root = ET.fromstring(r.read())
            break
        except Exception as e:   # network problems or rate limiting
            if attempt == 3:
                sys.exit(f"error: arXiv API unreachable ({e}); fall back to [verify]")
            time.sleep(5 * 2 ** attempt)
    hits = []
    for e in root.findall("a:entry", NS):
        ident = e.findtext("a:id", "", NS)
        hits.append({
            "id": ident,
            "url": ident.replace("http://", "https://"),
            "title": " ".join(e.findtext("a:title", "", NS).split()),
            "abstract": " ".join(e.findtext("a:summary", "", NS).split()),
            "date": e.findtext("a:published", "", NS)[:10],
            "authors": [a.findtext("a:name", "", NS) for a in e.findall("a:author", NS)],
        })
    return hits


def concept_query(query):
    words = [w for w in re.findall(r"[A-Za-z0-9]+", query) if w.lower() not in STOP and len(w) > 1]
    if not words:
        sys.exit("error: empty query after removing stopwords")
    return " AND ".join(f"all:{w}" for w in words[:8])


# ---------------------------------------------------------------- commands

def cmd_fingerprint(args):
    text = Path(args.paper).read_text(errors="replace")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    title = next((l for l in lines[:15] if 4 <= len(l.split()) <= 25 and not re.search(r"arxiv|@|http", l, re.I)), "")
    fp = {
        "title": title,
        "method_names": [],
        "authors": [],
        "arxiv_ids": sorted({m.group(0) for m in re.finditer(r"\b\d{4}\.\d{4,5}\b", text[:5000])}),
        "urls": sorted({u.rstrip(".,;)") for u in re.findall(r"https?://(?:github\.com|[\w.-]+\.github\.io)/[\w./-]+", text)})[:5],
        "distinctive_phrases": [],
        "cutoff_date": "",
        "_instructions": "Check the title; add method_names (e.g., the system's name), authors (if visible), "
                         "2-4 distinctive_phrases (6+ words from the abstract), and cutoff_date "
                         "(submission date, or arXiv v1 date, YYYY-MM-DD). Never use these in queries.",
    }
    Path(args.out).write_text(json.dumps(fp, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(fp, indent=2, ensure_ascii=False))


def ledger_path(args):
    return args.ledger or str(Path(args.fp).with_name("search_ledger.jsonl"))


def cmd_search(args):
    fp, ledger = load_fp(args.fp), ledger_path(args)
    reason = check_query(args.query, fp)
    if reason:
        ledger_write(ledger, {"event": "query_refused", "query": args.query, "reason": reason})
        sys.exit(f"refused: {reason}. Rephrase with problem/technique words only.")
    ledger_write(ledger, {"event": "query", "source": "arxiv", "query": args.query})
    hits = arxiv_query(concept_query(args.query), args.max)
    kept = filter_hits(hits, fp, args.mode, ledger, "arxiv")
    print(json.dumps({"query": args.query, "returned": len(hits), "kept": kept}, indent=2, ensure_ascii=False))


def cmd_filter(args):
    fp, ledger = load_fp(args.fp), ledger_path(args)
    hits = json.loads(Path(args.results).read_text())
    kept = filter_hits(hits, fp, args.mode, ledger, "external")
    print(json.dumps({"returned": len(hits), "kept": kept}, indent=2, ensure_ascii=False))


def cmd_verify(args):
    fp, ledger = load_fp(args.fp), ledger_path(args)
    words = [w for w in re.findall(r"[A-Za-z0-9]+", args.title) if w.lower() not in STOP and len(w) > 1]
    hits = arxiv_query(" AND ".join(f"ti:{w}" for w in dict.fromkeys(words[:8])), 5)
    best = max(hits, key=lambda h: difflib.SequenceMatcher(None, norm(h["title"]), norm(args.title)).ratio(), default=None)
    ratio = difflib.SequenceMatcher(None, norm(best["title"]), norm(args.title)).ratio() if best else 0
    result = {"title": args.title, "found": ratio >= 0.85}
    if result["found"]:
        if self_match(best, fp):
            result.update({"found": False, "note": "this is the reviewed paper itself; do not recommend it"})
        else:
            result.update({"arxiv_title": best["title"], "url": best["url"], "date": best["date"]})
    else:
        result["note"] = "not found on arXiv by title: keep [verify] (it may exist outside arXiv)"
    ledger_write(ledger, {"event": "verify", **{k: result.get(k) for k in ("title", "found", "url")}})
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description="Related-work search that never surfaces the reviewed paper.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("fingerprint"); p.add_argument("--paper", required=True); p.add_argument("--out", required=True)
    for name in ("search", "filter", "verify"):
        p = sub.add_parser(name)
        p.add_argument("--fp", required=True)
        p.add_argument("--ledger")
        if name == "search":
            p.add_argument("--query", required=True)
            p.add_argument("--max", type=int, default=25)
        if name == "filter":
            p.add_argument("--results", required=True)
        if name == "verify":
            p.add_argument("--title", required=True)
        if name in ("search", "filter"):
            p.add_argument("--mode", choices=("on", "strict"), default="on")
    args = ap.parse_args()
    {"fingerprint": cmd_fingerprint, "search": cmd_search,
     "filter": cmd_filter, "verify": cmd_verify}[args.cmd](args)


if __name__ == "__main__":
    main()
