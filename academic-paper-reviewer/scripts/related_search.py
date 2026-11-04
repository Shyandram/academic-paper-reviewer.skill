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
               [--purpose claim|baseline|expansion|general] [--tag C1]
      Query the arXiv API, filter the results, print kept results as JSON.
      --purpose and --tag (e.g., the claim ID) are logged for the audit.
      At most 12 queries per review (MAX_QUERIES); more are refused.

  filter       --fp fp.json --results hits.json [--mode on|strict]
      Filter results from another search tool (a JSON list of objects with
      title, url, snippet/abstract, date, authors).

  verify       --fp fp.json --title "Recommended reference title"
      Check that a recommended reference exists on arXiv (title match).

  benchmarks   --paper paper.txt [--fp fp.json]
      List the benchmarks and metrics the paper evaluates on (for the
      baseline scout). Benchmarks that are the paper's own (method_names)
      are marked: there is no prior state of the art to scout for them.

  scout        --fp fp.json --benchmark "ADE20K" [--metric mIoU]
      Search the kept results for prior work reporting on that benchmark,
      with the numbers its abstract gives. Only "prior" rows can be
      required baselines.

  coverage     --fp fp.json
      Summarize the searches so far: queries by purpose and claim tag,
      kept results by label and year, and gaps to fill in the expansion
      round (years with no prior work, claims with no query, no
      baseline query).

  similarity   --fp fp.json --paper paper.txt [--top 3]
      Score the reviewed paper against every kept result saved by search /
      filter (kept_results.jsonl): TF-IDF cosine for conceptual closeness and
      shared verbatim 8-word sequences for text overlap. Flags the closest
      prior works (novelty must be argued against them), high overlap
      (cosine >= 0.30) and text overlap (>= 2 shared 8-grams: an integrity
      concern for the editor, never an accusation).

Common option: --ledger search_ledger.jsonl (default: next to the fingerprint).

Filtering rules (see references/literature_search.md):
  drop  self-match: title similarity >= 0.8, a method name in title/abstract,
        a matching arXiv ID or URL, a distinctive phrase in the abstract, or
        >= 2 shared authors within 183 days of the cutoff
  drop  outcome-revealing pages: OpenReview forums, accepted-paper and award lists
  drop  post-cutoff results in strict mode; in "on" mode they are kept but
        labelled "newer" (never a required comparison)
  keep  everything else, labelled:
          prior (peer-reviewed)            publication evidence in journal_ref/comment
          prior (arXiv-only, 6+ months)    preprint posted >= 183 days before the cutoff
          recent preprint                  arXiv-only, < 6 months before: discuss only
          concurrent                       <= 60 days before the cutoff: discuss only
          newer                            after the cutoff ("on" mode): awareness only
        Only the two "prior" labels can be required comparisons.
"""

import argparse
import collections
import datetime as dt
import math
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
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
TITLE_SIM = 0.8
AUTHOR_WINDOW_DAYS = 183
CONCURRENT_DAYS = 60
PREPRINT_REQUIRED_DAYS = 183   # arXiv-only work counts as required prior work only if this old
PEER_REVIEWED = re.compile(
    r"(accepted|published|to appear|camera[- ]ready|proceedings)\b|"
    r"\b(CVPR|ICCV|ECCV|NeurIPS|NIPS|ICLR|ICML|AAAI|IJCAI|ACL|EMNLP|NAACL|MICCAI|WACV|BMVC|ACM ?MM|"
    r"SIGGRAPH|TPAMI|IJCV|TIP|TMLR|JMLR|Nature|Science)\s*['’]?\s*(19|20)?\d{2}\b", re.I)
HIGH_OVERLAP = 0.30      # calibrated: a paper vs. its own abstract ~0.55, related work <= 0.17
TEXT_OVERLAP_GRAMS = 2   # calibrated: own abstract shares ~33 8-grams, related work 0
GRAM = 8
MAX_QUERIES = 12         # one per contribution claim + baselines + an expansion round
PURPOSES = ("claim", "baseline", "expansion", "general")
METRICS = ["mIoU", "mAP", "AP50", "AP75", "AP", "AR", "PQ", "NDS", "PSNR", "SSIM", "LPIPS", "FID",
           "KID", "IS", "CLIP score", "CLIPScore", "FVD", "top-1", "top-5", "accuracy", "Recall@1",
           "R@1", "Recall@5", "R@5", "mAR", "Dice", "HD95", "EPE", "AbsRel", "RMSE", "Chamfer",
           "F-score", "AUC", "EER", "MOTA", "HOTA", "IDF1", "J&F", "BLEU", "CIDEr", "METEOR",
           "SPICE", "ROUGE", "mAcc", "gFID", "rFID", "IoU", "Acc", "CD", "OLS", "TOP", "DET", "success rate", "SR", "SPL", "NIQE"]
BENCHMARKS = ["COCO", "LVIS", "ADE20K", "Cityscapes", "ImageNet", "ImageNet-1K", "ImageNet-21K",
              "Pascal VOC", "PASCAL Context", "Objects365", "OpenImages", "nuScenes", "KITTI", "Waymo",
              "Argoverse", "OpenLane", "OpenLane-V2", "ScanNet", "ScanNet++", "ShapeNet", "ModelNet40",
              "DTU", "LLFF", "Mip-NeRF 360", "Tanks and Temples", "Replica", "CO3D", "Objaverse",
              "CIFAR-10", "CIFAR-100", "Kinetics", "Kinetics-400", "Something-Something", "UCF101",
              "HMDB51", "DAVIS", "YouTube-VOS", "MOT17", "MOT20", "Flickr30K", "MSCOCO", "VQAv2",
              "GQA", "TextVQA", "MMBench", "MME", "SEED-Bench", "RefCOCO", "RefCOCO+", "RefCOCOg",
              "CelebA", "CelebA-HQ", "FFHQ", "LSUN", "Set5", "Set14", "Urban100", "BSD100", "Manga109",
              "DIV2K", "GoPro", "SIDD", "LOL", "Rain100L", "Rain100H", "NYUv2", "SUN RGB-D",
              "Sintel", "FlyingThings", "M-BEIR", "ILIAS", "MSR-VTT", "ActivityNet", "Ego4D", "LAION",
              "PartNet", "PartNet-Mobility", "GSO", "OmniObject3D", "Mip-NeRF360", "BraTS", "Synapse", "ACDC", "ISIC", "CUB", "Stanford Cars", "Market-1501", "WIDER FACE"]
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
    if peer_reviewed(hit):
        return True, "prior (peer-reviewed)"
    if (cutoff - d).days >= PREPRINT_REQUIRED_DAYS:
        return True, "prior (arXiv-only, 6+ months before the cutoff)"
    return True, "recent preprint (arXiv-only, under 6 months before the cutoff; discuss, don't require)"


def peer_reviewed(hit):
    """True if the hit shows evidence of publication at a peer-reviewed venue."""
    if hit.get("peer_reviewed") is not None:
        return bool(hit["peer_reviewed"])
    if hit.get("journal_ref"):
        return True
    return bool(PEER_REVIEWED.search(f"{hit.get('comment', '')} {hit.get('venue', '')}"))


def kept_path(ledger):
    return str(Path(ledger).with_name("kept_results.jsonl"))


def filter_hits(hits, fp, mode, ledger, source):
    kept = []
    cache = open(kept_path(ledger), "a", encoding="utf-8")
    for h in hits:
        keep, label = classify(h, fp, mode)
        entry = {"title": h.get("title"), "date": h.get("date"), "url": h.get("url")}
        ledger_write(ledger, {"event": "keep" if keep else "drop", "source": source,
                              "reason": label, **entry})
        if keep:
            full = {**entry, "authors": h.get("authors", [])[:6], "label": label,
                    "venue_evidence": (h.get("journal_ref") or h.get("venue") or h.get("comment") or "")[:200],
                    "abstract": h.get("abstract") or h.get("snippet") or ""}
            cache.write(json.dumps(full, ensure_ascii=False) + "\n")
            kept.append({**full, "abstract": full["abstract"][:600]})
    cache.close()
    return kept


# ---------------------------------------------------------------- similarity

SIM_STOP = STOP | set("which these their its can also than such has have been show shows propose "
                      "proposed method methods paper results approach novel new".split())


def sim_tokens(text):
    return [w for w in norm(text).split() if w not in SIM_STOP and len(w) > 2]


def grams(text, n=GRAM):
    w = norm(text).split()
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def tfidf_cosines(target, docs):
    """Cosine of TF-IDF vectors; IDF is computed over the target plus candidates."""
    all_docs = [sim_tokens(target)] + [sim_tokens(d) for d in docs]
    df = collections.Counter(w for d in all_docs for w in set(d))
    n = len(all_docs)

    def vec(d):
        tf = collections.Counter(d)
        return {w: (c / max(len(d), 1)) * math.log((n + 1) / (df[w] + 1) + 1) for w, c in tf.items()}

    def cos(a, b):
        num = sum(v * b.get(w, 0.0) for w, v in a.items())
        den = math.sqrt(sum(v * v for v in a.values())) * math.sqrt(sum(v * v for v in b.values()))
        return num / den if den else 0.0

    t = vec(all_docs[0])
    return [cos(t, vec(d)) for d in all_docs[1:]]


def similarity_report(paper_text, kept, top=3):
    """Rank kept results by closeness to the paper and flag overlaps."""
    target = " ".join(paper_text.split()[:2500])        # abstract, intro and method
    paper_grams = grams(paper_text)
    seen, unique = set(), []
    for k in kept:                                     # de-duplicate repeated hits
        key = norm(k.get("title"))
        if key and key not in seen:
            seen.add(key)
            unique.append(k)
    cosines = tfidf_cosines(target, [k.get("abstract", "") for k in unique])
    rows = []
    for k, c in zip(unique, cosines):
        shared = sorted(grams(k.get("abstract", "")) & paper_grams)
        rows.append({"title": k.get("title"), "url": k.get("url"), "date": k.get("date"),
                     "label": k.get("label"), "cosine": round(c, 3),
                     "shared_8grams": len(shared), "examples": shared[:3]})
    rows.sort(key=lambda r: r["cosine"], reverse=True)
    prior_rank = [r for r in rows if str(r["label"]).startswith("prior")]
    for r in rows:
        flags = []
        if r in prior_rank[:top]:
            flags.append("closest prior work: argue novelty against it")
        if r["cosine"] >= HIGH_OVERLAP:
            flags.append("high conceptual overlap: check task and core mechanism")
        if r["shared_8grams"] >= TEXT_OVERLAP_GRAMS:
            flags.append("text overlap: verbatim passages shared; report as an integrity concern to the editor")
        r["flags"] = flags
    return rows



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
            "comment": " ".join((e.findtext("arxiv:comment", "", NS) or "").split()),
            "journal_ref": " ".join((e.findtext("arxiv:journal_ref", "", NS) or "").split()),
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


def read_ledger(ledger):
    p = Path(ledger)
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def cmd_search(args):
    fp, ledger = load_fp(args.fp), ledger_path(args)
    reason = check_query(args.query, fp)
    if reason:
        ledger_write(ledger, {"event": "query_refused", "query": args.query, "reason": reason})
        sys.exit(f"refused: {reason}. Rephrase with problem/technique words only.")
    sent = sum(e.get("event") == "query" for e in read_ledger(ledger))
    if sent >= MAX_QUERIES:
        ledger_write(ledger, {"event": "query_over_budget", "query": args.query})
        sys.exit(f"refused: query budget reached ({MAX_QUERIES}). Use the results you have.")
    ledger_write(ledger, {"event": "query", "source": "arxiv", "query": args.query,
                          "purpose": args.purpose, "tag": args.tag})
    hits = arxiv_query(concept_query(args.query), args.max)
    kept = filter_hits(hits, fp, args.mode, ledger, "arxiv")
    ledger_write(ledger, {"event": "query_result", "query": args.query, "purpose": args.purpose,
                          "tag": args.tag, "returned": len(hits), "kept": len(kept)})
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

# ---------------------------------------------------------------- baseline scout

def term_re(term, case=False):
    body = r"[\s-]?".join(re.escape(w) for w in str(term).split())
    return re.compile(rf"(?<![A-Za-z0-9]){body}(?![A-Za-z0-9])", 0 if case else re.I)


def find_benchmarks(text, fp=None):
    """Benchmarks (from a known list) the paper mentions, most frequent first, with nearby metrics.

    Matching is case-sensitive; a longer name (ImageNet-1K) claims its span before a
    shorter one (ImageNet). The paper's own new benchmarks are not in the list: add them
    by hand and mark them own (nothing to scout)."""
    own = {norm(n) for n in (fp or {}).get("method_names", [])}
    taken, found = [], []
    for name in sorted(set(BENCHMARKS), key=len, reverse=True):
        spans = [m.span() for m in term_re(name, case=True).finditer(text)
                 if not any(a <= m.start() < b for a, b in taken)]
        if spans:
            taken += spans
            found.append({"benchmark": name, "mentions": len(spans), "own": norm(name) in own})
    lines = text.splitlines()
    for f in found:
        near = collections.Counter()
        for i, line in enumerate(lines):
            if term_re(f["benchmark"], case=True).search(line):
                window = " ".join(lines[max(0, i - 1): i + 2]) if len(lines) > 3 else line
                near.update(m for m in METRICS if term_re(m, case=True).search(window))
        f["metrics"] = [m for m, _ in near.most_common(4)]
    found.sort(key=lambda f: f["mentions"], reverse=True)
    return found


def scout_rows(kept, benchmark, metric=None):
    """Kept results whose abstract reports on the benchmark, with the numbers it gives."""
    b_re, m_re = term_re(benchmark), term_re(metric) if metric else None
    seen, rows = set(), []
    for k in kept:
        key = norm(k.get("title"))
        text = k.get("abstract", "")
        if key in seen or not b_re.search(text + " " + str(k.get("title", ""))):
            continue
        seen.add(key)
        sentences = [x for x in re.split(r"(?<=[.;])\s+", text) if b_re.search(x)] or [k.get("title", "")]
        evidence = sentences[0][:300]
        numbers = [n.replace(" ", "") for n in re.findall(r"\b\d{1,3}(?:\.\d+)?(?:\s?%)?", " ".join(sentences))]
        label = str(k.get("label"))
        rows.append({"title": k.get("title"), "url": k.get("url"), "date": k.get("date"), "label": label,
                     "can_be_required": label.startswith("prior"),
                     "metric_mentioned": bool(m_re and m_re.search(" ".join(sentences))),
                     "numbers": numbers[:6], "evidence": evidence})
    rows.sort(key=lambda r: (not r["can_be_required"], not r["metric_mentioned"], str(r["date"])))
    return rows


def short_label(label):
    label = str(label)
    if label.startswith("prior (peer"):
        return "prior (peer-reviewed)"
    if label.startswith("prior"):
        return "prior (arXiv-only)"
    return label.split(" (")[0]


def coverage_report(events, kept, fp, claims=None):
    queries = [e for e in events if e.get("event") == "query"]
    by_purpose = collections.Counter(e.get("purpose") or "general" for e in queries)
    tags = sorted({e.get("tag") for e in queries if e.get("tag")})
    seen, uniq = set(), []
    for k in kept:
        key = norm(k.get("title"))
        if key not in seen:
            seen.add(key)
            uniq.append(k)
    labels = collections.Counter(short_label(k.get("label")) for k in uniq)
    years = collections.Counter(d.year for d in (parse_date(k.get("date")) for k in uniq
                                                 if str(k.get("label")).startswith("prior")) if d)
    cutoff = parse_date(fp["cutoff_date"]).year
    gaps = []
    window = range(cutoff - 4, cutoff + 1)
    empty = [y for y in window if not years.get(y)]
    if empty:
        gaps.append(f"no prior work kept from {', '.join(map(str, empty))}: check for foundational or recent work there")
    if not by_purpose.get("baseline"):
        gaps.append("no baseline query yet: run one per benchmark from the benchmarks command")
    if not by_purpose.get("claim"):
        gaps.append("no claim query yet: run one per contribution claim (--purpose claim --tag C1 ...)")
    for c in claims or []:
        if c not in tags:
            gaps.append(f"claim {c} has no query")
    kept_by_tag = collections.Counter()
    for e in events:
        if e.get("event") == "query_result" and e.get("tag"):
            kept_by_tag[e["tag"]] += e.get("kept", 0)
    for t in tags:
        if t in {e.get("tag") for e in events if e.get("event") == "query_result"} and not kept_by_tag[t]:
            gaps.append(f"claim {t}: its queries kept no results; rephrase with broader task words")
    return {"queries": len(queries), "budget": MAX_QUERIES, "by_purpose": dict(by_purpose),
            "claim_tags": tags, "unique_kept": len(uniq), "kept_by_label": dict(labels),
            "prior_by_year": {str(y): years[y] for y in sorted(years)}, "gaps": gaps}


def load_kept(ledger):
    p = Path(kept_path(ledger))
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def cmd_benchmarks(args):
    fp = json.loads(Path(args.fp).read_text()) if args.fp else None
    rows = find_benchmarks(Path(args.paper).read_text(errors="replace"), fp)
    print(json.dumps({"benchmarks": rows,
                      "note": "Confirm against the paper's tables. Scout each benchmark that is not the "
                              "paper's own: search --purpose baseline, then scout --benchmark."},
                     indent=2, ensure_ascii=False))


def cmd_scout(args):
    fp, ledger = load_fp(args.fp), ledger_path(args)
    if any(norm(args.benchmark) == norm(n) for n in fp["method_names"]):
        sys.exit("refused: this benchmark is the paper's own; there is no prior state of the art to scout")
    rows = scout_rows(load_kept(ledger), args.benchmark, args.metric)
    ledger_write(ledger, {"event": "scout", "benchmark": args.benchmark, "metric": args.metric,
                          "rows": len(rows), "required_candidates": sum(r["can_be_required"] for r in rows)})
    print(json.dumps({"benchmark": args.benchmark, "metric": args.metric, "rows": rows,
                      "note": "Abstract numbers are pointers, not verified results: check the setting "
                              "(backbone, data, split) before calling a baseline missing or under-reported."},
                     indent=2, ensure_ascii=False))


def cmd_coverage(args):
    fp, ledger = load_fp(args.fp), ledger_path(args)
    claims = [c.strip() for c in (args.claims or "").split(",") if c.strip()]
    print(json.dumps(coverage_report(read_ledger(ledger), load_kept(ledger), fp, claims),
                     indent=2, ensure_ascii=False))


def cmd_similarity(args):
    fp, ledger = load_fp(args.fp), ledger_path(args)
    path = kept_path(ledger)
    if not Path(path).exists():
        sys.exit("error: no kept results yet; run search (or filter) first")
    kept = [json.loads(l) for l in Path(path).read_text().splitlines() if l.strip()]
    rows = similarity_report(Path(args.paper).read_text(errors="replace"), kept, args.top)
    flagged = [r for r in rows if r["flags"]]
    ledger_write(ledger, {"event": "similarity", "candidates": len(rows),
                          "flagged": [(r["title"], r["cosine"], r["shared_8grams"]) for r in flagged]})
    print(json.dumps({"candidates": len(rows), "flagged": flagged,
                      "thresholds": {"high_overlap_cosine": HIGH_OVERLAP,
                                     "text_overlap_8grams": TEXT_OVERLAP_GRAMS}},
                     indent=2, ensure_ascii=False))


def main():
    ap = argparse.ArgumentParser(description="Related-work search that never surfaces the reviewed paper.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("fingerprint"); p.add_argument("--paper", required=True); p.add_argument("--out", required=True)
    p = sub.add_parser("similarity"); p.add_argument("--fp", required=True); p.add_argument("--paper", required=True)
    p.add_argument("--ledger"); p.add_argument("--top", type=int, default=3)
    p = sub.add_parser("benchmarks"); p.add_argument("--paper", required=True); p.add_argument("--fp")
    p.add_argument("--ledger", help="accepted for consistency; benchmarks does not log")
    p = sub.add_parser("scout"); p.add_argument("--fp", required=True); p.add_argument("--ledger")
    p.add_argument("--benchmark", required=True); p.add_argument("--metric")
    p = sub.add_parser("coverage"); p.add_argument("--fp", required=True); p.add_argument("--ledger")
    p.add_argument("--claims", help="comma-separated claim tags, e.g. C1,C2,C3")
    for name in ("search", "filter", "verify"):
        p = sub.add_parser(name)
        p.add_argument("--fp", required=True)
        p.add_argument("--ledger")
        if name == "search":
            p.add_argument("--query", required=True)
            p.add_argument("--max", type=int, default=25)
            p.add_argument("--purpose", choices=PURPOSES, default="general")
            p.add_argument("--tag")
        if name == "filter":
            p.add_argument("--results", required=True)
        if name == "verify":
            p.add_argument("--title", required=True)
        if name in ("search", "filter"):
            p.add_argument("--mode", choices=("on", "strict"), default="on")
    args = ap.parse_args()
    {"fingerprint": cmd_fingerprint, "search": cmd_search, "filter": cmd_filter,
     "verify": cmd_verify, "similarity": cmd_similarity, "benchmarks": cmd_benchmarks,
     "scout": cmd_scout, "coverage": cmd_coverage}[args.cmd](args)


if __name__ == "__main__":
    main()
