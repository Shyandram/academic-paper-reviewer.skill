#!/usr/bin/env python3
"""ICLR score calibration, following the paperreview.ai (Stanford Agentic Reviewer) protocol.

Default: ICLR 2026, which is newer than most model training data and so less likely to
be memorized. paperreview.ai used ICLR 2025; that is still available with --year 2025
--source berens.

Protocol (paperreview.ai/tech-overview, ICLR 2025):
  randomly sample 300 submissions, drop withdrawn / desk-rejected ones that have no human
  scores, train a linear regression on 150 that maps the 7 dimension scores to one score,
  and test on the rest. Test metrics: Spearman(AI score, one human score), with
  Spearman(one human, another human) as the baseline; AUC for predicting acceptance from
  one human score and from the AI score. Reference numbers from that page: Spearman 0.41
  for human vs human and 0.42 for AI vs human; AUC 0.84 for one human score and 0.75 for
  the AI score. The human AUC is inflated, because decisions were partly made from
  those same scores.

Subcommands (standard library only, except `sample`, which reads parquet via pyarrow):

  sample    python3 -I evals/iclr_calibration.py sample jerma.parquet \
                --out evals/work/benchmarks/iclr2026/sample.jsonl
            2026 source: huggingface.co/datasets/JerMa88/ICLR_Peer_Reviews_2026
            (every submission, including withdrawn ones). 2025 source:
            github.com/berenslab/iclr-dataset (--source berens; its 2026 file predates reviews).
  find      python3 -I evals/iclr_calibration.py find sample.jsonl
            Matches each title on export.arxiv.org and downloads v1, the version closest
            to submission. Writes blinded text to evals/work/papers/iclr<yy>-<id>/.
  features  python3 -I evals/iclr_calibration.py features evals/work/results --out features.jsonl
  evaluate  python3 -I evals/iclr_calibration.py evaluate sample.jsonl features.jsonl
            features.jsonl: {"paper_id", "dims": {7 dimension keys: 0-100}}, one per line,
            for example from each run's aggregate.json.

The sample file holds human scores and decisions. It is ground truth, so it stays under
evals/work/ (git-ignored) and is never shown to the reviewer agents.
"""

import argparse
import json
import math
import os
import random
import re
import statistics
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_papers import blind  # noqa: E402

DIMS = ["technical_rigor", "clarity", "novelty", "significance",
        "experimental_validation", "reproducibility", "ethics"]
WORK = Path(__file__).resolve().parent / "work" / "papers"
ICLR_YEAR_MARK = re.compile(r"\b(published as a conference paper at|under review as a conference "
                            r"paper at)\b[^\n]*|\biclr[\s_-]?(20\d\d|'\d\d)\b", re.I)


# ---------- sample ----------

def accepted(decision):
    return decision.lower().startswith(("accept", "conditional accept"))


def draw(rows, n=300, train=150, seed=2025):
    """Sample n from all submissions, then exclude those with no scores (withdrawn or
    desk rejected). This is the paperreview.ai order: 300 sampled, 297 kept."""
    rng = random.Random(seed)
    picked = rng.sample(sorted(rows, key=lambda r: r["paper_id"]), min(n, len(rows)))
    kept = [r for r in picked if r["scores"]]
    for i, r in enumerate(kept):
        r["split"] = "train" if i < train else "test"
        # "One human score": a seeded random reviewer, plus a second reviewer for the
        # human-human baseline. Both are fixed now so every later run uses the same ones.
        order = rng.sample(range(len(r["scores"])), len(r["scores"]))
        r["one_human"] = r["scores"][order[0]]
        r["other_human"] = r["scores"][order[1]] if len(order) > 1 else None
    return picked, kept


def rows_berens(path, year):
    """berenslab/iclr-dataset: one row per submission, scores as a list."""
    import pyarrow.parquet as pq
    d = pq.read_table(path).to_pydict()
    return [{"paper_id": d["id"][i], "title": d["title"][i], "decision": d["decision"][i],
             "accepted": accepted(d["decision"][i]), "scores": list(d["scores"][i] or [])}
            for i in range(len(d["id"])) if d["year"][i] == year]


def rows_jerma(path):
    """JerMa88/ICLR_Peer_Reviews_2026: one row per review. Withdrawn and desk-rejected
    submissions have decision "Unknown"; their venue field says which. Those with scores
    are kept as not accepted, as in the paperreview.ai protocol."""
    import pyarrow.parquet as pq
    cols = ["paper_id", "title", "decision", "rating", "reviewer_id", "review_src",
            "api_raw_submission"]
    t = pq.read_table(path, columns=cols).to_pydict()
    papers = {}
    for i, pid in enumerate(t["paper_id"]):
        p = papers.setdefault(pid, {"paper_id": pid, "title": t["title"][i],
                                    "decision": t["decision"][i], "scores": [], "_seen": set(),
                                    "primary_area": None})
        if p["primary_area"] is None and t["api_raw_submission"][i]:
            try:
                area = json.loads(t["api_raw_submission"][i])["content"].get("primary_area")
                p["primary_area"] = area.get("value") if isinstance(area, dict) else area
            except (ValueError, KeyError, TypeError, AttributeError):
                pass
        if p["decision"] == "Unknown" and t["api_raw_submission"][i]:
            try:
                venue = json.loads(t["api_raw_submission"][i])["content"]["venue"]["value"]
                p["decision"] = ("Desk rejected" if "Desk Rejected" in venue
                                 else "Withdrawn" if "Withdrawn" in venue else "Unknown")
            except (ValueError, KeyError, TypeError):
                pass
        rid = t["reviewer_id"][i]
        if t["review_src"][i] == "openreview" and t["rating"][i] is not None \
                and rid not in p["_seen"]:
            p["_seen"].add(rid)
            p["scores"].append(t["rating"][i])
    out = []
    for p in papers.values():
        del p["_seen"]
        p["accepted"] = accepted(p["decision"])
        out.append(p)
    return out


def cmd_sample(a):
    rows = rows_jerma(a.parquet) if a.source == "jerma" else rows_berens(a.parquet, a.year)
    picked, kept = draw(rows, a.n, a.train, a.seed)
    for r in kept:
        r["mean_human"] = round(statistics.mean(r["scores"]), 3)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in kept))
    acc = sum(r["accepted"] for r in kept)
    print(f"{len(rows)} ICLR {a.year} submissions; sampled {len(picked)}, excluded "
          f"{len(picked) - len(kept)} with no scores; kept {len(kept)} ({acc} accepted); "
          f"train {sum(r['split'] == 'train' for r in kept)}, "
          f"test {sum(r['split'] == 'test' for r in kept)}", file=sys.stderr)


# ---------- find ----------

def norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def arxiv_query(q):
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": q, "max_results": 5})
    req = urllib.request.Request(url, headers={"User-Agent": "paper-review-eval/1.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        root = ET.fromstring(r.read())
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    for e in root.findall("a:entry", ns):
        aid = e.findtext("a:id", "", ns).rsplit("/abs/", 1)[-1]
        out.append({"arxiv_id": re.sub(r"v\d+$", "", aid),
                    "title": " ".join(e.findtext("a:title", "", ns).split()),
                    "published": e.findtext("a:published", "", ns)[:10]})
    return out


def arxiv_search(title):
    """Exact title phrase first; if that finds nothing, the leading title words OR-ed
    (best_match then filters by similarity). A plain AND of words often returns nothing."""
    hits = arxiv_query(f'ti:"{norm_title(title)}"')
    if not hits:
        time.sleep(3)
        words = [w for w in norm_title(title).split() if len(w) > 3][:8]
        hits = arxiv_query(" AND ".join(f"ti:{w}" for w in words[:4])) if words else []
    return hits


def best_match(title, hits, threshold=0.92):
    scored = [(SequenceMatcher(None, norm_title(title), norm_title(h["title"])).ratio(), h)
              for h in hits]
    scored.sort(key=lambda s: -s[0])
    return scored[0][1] if scored and scored[0][0] >= threshold else None


# Approximate dates: full-paper deadline (literature cutoff) and decision notification.
DATES = {2025: ("2024-10-01", "2025-01-22"), 2026: ("2025-09-24", "2026-01-26")}


def cmd_find(a):
    a.decision_date = a.decision_date or DATES[a.year][1]
    rows = [json.loads(l) for l in open(a.sample)]
    if a.split != "all":
        rows = [r for r in rows if r["split"] == a.split]
    rows = rows[a.offset:a.offset + a.limit] if a.limit else rows[a.offset:]
    found = []
    for r in rows:
        d = WORK / f"iclr{a.year % 100}-{r['paper_id']}"
        meta = d / "arxiv.json"
        if meta.exists():
            hit = json.loads(meta.read_text())
        else:
            try:
                hit = best_match(r["title"], arxiv_search(r["title"]))
            except Exception as e:  # network: report and continue
                print(f"  search failed {r['paper_id']}: {e}", file=sys.stderr)
                continue
            finally:
                time.sleep(3)  # arXiv API etiquette
            d.mkdir(parents=True, exist_ok=True)
            meta.write_text(json.dumps(hit))
        if not hit and a.openreview:
            # Fallback: the OpenReview PDF (submission version for rejected papers,
            # camera-ready for accepted ones). Blocked in some sandboxes.
            hit = {"arxiv_id": None, "published": "", "source": "openreview"}
        if not hit:
            continue
        pdf = d / ("arxiv.pdf" if hit["arxiv_id"] else "openreview.pdf")
        if not pdf.exists():
            url = (f"https://export.arxiv.org/pdf/{hit['arxiv_id']}v1" if hit["arxiv_id"]
                   else f"https://openreview.net/pdf?id={r['paper_id']}")
            req = urllib.request.Request(url, headers={"User-Agent": "paper-review-eval/1.0"})
            try:
                with urllib.request.urlopen(req, timeout=120) as resp:
                    pdf.write_bytes(resp.read())
            except Exception as e:
                print(f"  pdf failed {r['paper_id']}: {e}", file=sys.stderr)
                continue
            time.sleep(3)
        if pdf.read_bytes()[:5] != b"%PDF-":
            pdf.unlink()
            continue
        extract_text(d, pdf.read_bytes(), r["title"])
        hit["post_decision"] = bool(hit["published"]) and hit["published"] > a.decision_date
        hit.setdefault("source", "arxiv")
        found.append((r, hit))
    report_coverage(rows, found)
    if a.ids_out:
        Path(a.ids_out).write_text(json.dumps([f"iclr{a.year % 100}-{r['paper_id']}"
                                               for r, _ in found]))


def report_coverage(rows, found):
    by = {s: [r for r in rows if r["split"] == s] for s in ("train", "test")}
    got = {r["paper_id"] for r, _ in found}
    for s, rs in by.items():
        for lab, sub in (("accepted", [r for r in rs if r["accepted"]]),
                         ("rejected", [r for r in rs if not r["accepted"]])):
            k = sum(r["paper_id"] in got for r in sub)
            print(f"{s} {lab}: {k}/{len(sub)} with arXiv text", file=sys.stderr)
    src = sum(h["source"] == "openreview" for _, h in found)
    print(f"{src}/{len(found)} from the OpenReview fallback", file=sys.stderr)
    late = sum(h["post_decision"] for _, h in found)
    print(f"{late}/{len(found)} first appeared on arXiv after the decision date "
          f"(outcome-leak risk; flag them in the report)", file=sys.stderr)


# ---------- pdfs (paperreview.ai dump) ----------

HF = "https://huggingface.co/datasets/paperreview/"
# ICLR 2026 PDFs published by paperreview.ai, named <openreview id>.pdf. Batches 1-28
# are in the gated repos (accept the terms on huggingface.co and use a token);
# batches 29-40 are public.
BATCHES = [(repo, b) for b in range(1, 41)
           for repo in (("ICLR2026-part2",) if b > 28 else ("ICLR2026", "ICLR2026-part1"))]


ABSTRACT_HEAD = re.compile(r"^\s*(A\s?BSTRACT|Abstract|ABSTRACT)\s*$", re.M)
ARXIV_STAMP = re.compile(r"arXiv:\d{4}\.\d{4,5}(v\d+)?\s*\[[^\]\n]+\]\s*\d{1,2}\s+\w{3}\s+\d{4}")
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")
LINK = re.compile(r"(https?://)?(www\.)?(github\.com|gitlab\.com|huggingface\.co|"
                  r"anonymous\.4open\.science|[\w-]+\.github\.io|sites\.google\.com)[^\s)\]}>,;]*")
AFFILIATION = re.compile(r"(universit|institut|department|laborator|school of|college|"
                         r"equal contribution|corresponding author|work done (while|during))", re.I)
FOOTNOTE_MARK = re.compile(r"^\s*([*†‡§¶∗]|\d\s)")
ACKS = re.compile(r"\n[ \t]*(\d+[ \t]+)?(A\s?CKNOWLEDG\w*|Acknowledg\w*)[^\n]*\n.*?"
                  r"(?=\n[ \t]*(R\s?EFERENCES|References|Bibliography|R\s?EFERENCE)\b)", re.S)
ACCEPT_MARK = re.compile(r"\b(accepted|to appear|published)\s+(at|in|to|by|as)\b[^\n]{0,80}", re.I)
LINE_NO = re.compile(r"^[ \t]{0,8}\d{3}(?=[ \t]{2,}|[ \t]*$)", re.M)


def normalize(text, title):
    """Make every paper look the same whatever its source or decision. Replaces the
    pre-abstract header (title, authors, affiliations, "Anonymous authors") with the
    OpenReview title, and removes line numbers, the arXiv stamp, emails, affiliation
    footnotes, author code links, acknowledgments and acceptance marks. Returns the
    text and a count of each removal."""
    n = {}

    def sub(name, pat, repl, t, **kw):
        t, k = pat.subn(repl, t, **kw)
        n[name] = n.get(name, 0) + k
        return t
    text = sub("arxiv_stamp", ARXIV_STAMP, "", text)
    # Submission line numbers: only when the document is numbered throughout.
    if len(LINE_NO.findall(text)) > 100:
        text = sub("line_numbers", LINE_NO, "", text)
    m = ABSTRACT_HEAD.search(text, 0, 8000)
    if m:
        text = f"{title}\n\n[Author block removed]\n\n" + text[m.start():]
        n["header"] = 1
    else:
        text = f"{title}\n\n" + text
        n["header"] = 0
    lines = text.split("\n")
    head = min(len(lines), 400)
    keep = [l for i, l in enumerate(lines) if not (
        i < head and AFFILIATION.search(l) and (EMAIL.search(l) or FOOTNOTE_MARK.match(l)))]
    n["affiliation_lines"] = len(lines) - len(keep)
    text = "\n".join(keep)
    text = sub("emails", EMAIL, "[email removed]", text)
    text = sub("links", LINK, "[link removed]", text)
    text = sub("acknowledgments", ACKS, "\n[Acknowledgments removed]\n", text)
    front, rest = text[:4000], text[4000:]
    front = sub("accept_marks", ACCEPT_MARK, "[REDACTED: venue/acceptance mark]", front)
    text = front + rest
    text, k = blind(text)
    text, k2 = ICLR_YEAR_MARK.subn("[REDACTED: venue/acceptance mark]", text)
    n["venue_marks"] = k + k2
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text, n


def extract_text(d, pdf_bytes, title=""):
    """Write paper.pdf, paper.txt and the normalized, blinded text the reviewers read."""
    d.mkdir(parents=True, exist_ok=True)
    pdf = d / "paper.pdf"
    pdf.write_bytes(pdf_bytes)
    txt = d / "paper.txt"
    subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=True)
    text, n = normalize(txt.read_text(errors="replace"), title)
    (d / "blinded.txt").write_text(text)
    (d / "normalize.json").write_text(json.dumps(n))


def cmd_pdfs(a):
    """Stream the batches and keep only sampled papers; nothing else touches the disk."""
    import tarfile
    rows = [json.loads(l) for l in open(a.sample)]
    want = {r["paper_id"] for r in rows}
    titles = {r["paper_id"]: r["title"] for r in rows}
    done = {pid for pid in want
            if (WORK / f"iclr{a.year % 100}-{pid}" / "source.json").exists()}
    batches = [(repo, b) for repo, b in BATCHES if b in set(a.batches)] if a.batches else BATCHES
    headers = {"User-Agent": "paper-review-eval/1.0"}
    if os.environ.get("HF_TOKEN"):
        headers["Authorization"] = "Bearer " + os.environ["HF_TOKEN"]
    for repo, b in batches:
        if want <= done:
            break
        url = f"{HF}{repo}/resolve/main/pdfs_batch_{b}.tar.gz"
        n = 0
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers),
                                        timeout=120) as resp, \
                    tarfile.open(fileobj=resp, mode="r|gz") as tar:
                for m in tar:
                    pid = Path(m.name).stem
                    if not m.isfile() or pid not in want or pid in done:
                        continue
                    d = WORK / f"iclr{a.year % 100}-{pid}"
                    extract_text(d, tar.extractfile(m).read(), titles.get(pid, ""))
                    (d / "source.json").write_text(json.dumps({"source": f"{repo}/batch_{b}"}))
                    done.add(pid)
                    n += 1
        except Exception as e:  # gated batch without a token, or network
            print(f"batch {b} ({repo}): {e}", file=sys.stderr)
            continue
        print(f"batch {b}: {n} sampled papers; {len(done)}/{len(want)} so far", file=sys.stderr)
    print(f"{len(done)}/{len(want)} sampled papers have the submission PDF", file=sys.stderr)


# ---------- sources / fetch (reproducible text on another machine) ----------

def cmd_sources(a):
    """Record where each sampled paper's text came from: an arXiv v1 posted before the
    decision (one source format for every decision group), or with --dump a dump batch.
    The map has IDs only, no text and no labels, so it can be committed and used by
    `fetch` on a CI runner."""
    rows = [json.loads(l) for l in open(a.sample)]
    out, late = {}, 0
    for r in rows:
        d = WORK / f"iclr{a.year % 100}-{r['paper_id']}"
        if not (d / "blinded.txt").exists():
            continue
        if a.dump and (d / "source.json").exists():
            out[r["paper_id"]] = json.loads((d / "source.json").read_text())["source"]
        elif (d / "arxiv.json").exists() and json.loads((d / "arxiv.json").read_text()):
            hit = json.loads((d / "arxiv.json").read_text())
            if hit["published"] > (a.decision_date or DATES[a.year][1]):
                late += 1  # first posted after the decision: may be revised; outcome leak
                continue
            out[r["paper_id"]] = "arxiv:" + hit["arxiv_id"]
    if late:
        print(f"{late} arXiv papers first posted after the decision date were left out",
              file=sys.stderr)
    Path(a.out).write_text(json.dumps(dict(sorted(out.items())), indent=0) + "\n")
    print(f"{len(out)}/{len(rows)} sampled papers have a text source", file=sys.stderr)


def group(r):
    d = r["decision"]
    return "accepted" if accepted(d) else {"Withdrawn": "withdrawn",
                                           "Desk rejected": "desk rejected"}.get(d, "rejected")


def stratified(rows, candidates, n, seed=0, prefer=()):
    """Pick n candidates that are representative of `rows` (the whole sample):
    decision groups in the sample's proportions (largest remainder), and within each
    group one paper per quantile of the mean human score, preferring primary areas
    and text sources not used yet."""
    rng = random.Random(seed)
    share = {}
    for r in rows:
        share[group(r)] = share.get(group(r), 0) + 1
    raw = {g: n * k / len(rows) for g, k in share.items()}
    quota = {g: int(v) for g, v in raw.items()}
    for g in sorted(raw, key=lambda g: raw[g] - quota[g], reverse=True)[:n - sum(quota.values())]:
        quota[g] += 1
    picked, areas, sources = [], {}, {}
    for g in sorted(quota):
        pool = sorted((c for c in candidates if group(c) == g), key=lambda c: c["mean_human"])
        q = min(quota[g], len(pool))
        for k in range(q):
            chunk = pool[k * len(pool) // q:(k + 1) * len(pool) // q]
            rng.shuffle(chunk)
            best = min(chunk, key=lambda c: (c["paper_id"] not in prefer,
                                             areas.get(c.get("primary_area"), 0),
                                             sources.get(c.get("source_kind"), 0)))
            picked.append(best)
            areas[best.get("primary_area")] = areas.get(best.get("primary_area"), 0) + 1
            sources[best.get("source_kind")] = sources.get(best.get("source_kind"), 0) + 1
    return picked


def balanced(rows, candidates, seed=0, prefer=()):
    """Fairness for a partial-text sample. Keep the largest subset of `candidates` whose
    decision mix matches the whole sample `rows` (spread over human-score quantiles via
    stratified), then split it into train and test halves with a seed, stratified by
    decision group, so both halves have the sample's mix. The original split was random
    too; nothing has been reviewed when this runs, so re-splitting costs nothing."""
    share, have = {}, {}
    for r in rows:
        share[group(r)] = share.get(group(r), 0) + 1
    for c in candidates:
        have[group(c)] = have.get(group(c), 0) + 1
    n = len(candidates)
    while n and any(round(n * k / len(rows)) > have.get(g, 0) for g, k in share.items()):
        n -= 1
    kept = stratified(rows, candidates, n, seed, prefer)
    # A preferred (already reviewed) paper may still lose its quantile slot to another
    # preferred one; report it rather than silently dropping paid work.
    lost = set(prefer) & {c["paper_id"] for c in candidates} - {r["paper_id"] for r in kept}
    if lost:
        print(f"  note: {len(lost)} reviewed papers fall outside the balanced set", file=sys.stderr)
    rng = random.Random(seed + 1)
    out = []
    for g in sorted({group(r) for r in kept}):
        members = sorted((r for r in kept if group(r) == g), key=lambda r: r["paper_id"])
        rng.shuffle(members)
        for i, r in enumerate(members):
            out.append(dict(r, split="train" if i % 2 == 0 else "test"))
    return sorted(out, key=lambda r: (r["split"] != "train", r["paper_id"]))


def coverage_report(rows, have):
    """Per decision group: share with text, and mean human score with vs without text."""
    lines = []
    for g in ("accepted", "rejected", "withdrawn", "desk rejected"):
        rs = [r for r in rows if group(r) == g]
        w = [r["mean_human"] for r in rs if r["paper_id"] in have]
        wo = [r["mean_human"] for r in rs if r["paper_id"] not in have]
        lines.append(f"{g:14s} {len(w):3d}/{len(rs):3d} with text; mean human "
                     f"{statistics.mean(w) if w else float('nan'):.2f} with vs "
                     f"{statistics.mean(wo) if wo else float('nan'):.2f} without")
    return "\n".join(lines)


def cmd_fetch(a):
    """Download the text for the selected rows from the committed source map."""
    import tarfile
    rows = [json.loads(l) for l in open(a.sample)]
    if a.split != "all":
        rows = [r for r in rows if r["split"] == a.split]
    src = json.load(open(a.sources))
    everyone = [json.loads(l) for l in open(a.sample)]
    rows = [r for r in rows if r["paper_id"] in src]  # offset/limit count papers with text
    for r in rows:
        r["source_kind"] = "arxiv" if src[r["paper_id"]].startswith("arxiv:") else "dump"
    if a.pick in ("stratified", "balanced"):
        print(coverage_report(everyone, set(src)), file=sys.stderr)
    reviewed = set(json.load(open(a.reviewed))) if a.reviewed else set()
    prefer = reviewed | (set(json.load(open(a.prefer))) if a.prefer else set())
    if a.pick in ("balanced", "stratified"):
        rows = balanced(everyone, rows, prefer=prefer)
        if a.splits_out:
            Path(a.splits_out).write_text(json.dumps({r["paper_id"]: r["split"] for r in rows}))
    if a.pick == "balanced":
        rows = [r for r in rows if r["paper_id"] not in reviewed]  # already have results
        rows = rows[a.offset:a.offset + a.limit] if a.limit else rows[a.offset:]
    if a.pick == "stratified":  # pilot: drawn from the balanced set, so its runs count later
        rows = stratified(everyone, rows, a.limit or len(rows), prefer=prefer)
        for r in rows:
            print(f"  pick {r['paper_id']}: {group(r)}, {r['split']}, mean {r['mean_human']}, "
                  f"{r['source_kind']}, {r.get('primary_area')}", file=sys.stderr)
    else:
        rows = rows[a.offset:a.offset + a.limit] if a.limit else rows[a.offset:]
    need = {r["paper_id"]: src[r["paper_id"]] for r in rows}
    titles = {r["paper_id"]: r["title"] for r in rows}
    if a.dry_run:  # selection only: write ids and splits without downloading
        if a.ids_out:
            Path(a.ids_out).write_text(json.dumps([f"iclr{a.year % 100}-{p}" for p in need]))
        return
    got = []
    by_batch = {}
    for pid, s in need.items():
        if s.startswith("arxiv:"):
            url = f"https://export.arxiv.org/pdf/{s[6:]}v1"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "paper-review-eval/1.0"})
                with urllib.request.urlopen(req, timeout=120) as resp:
                    data = resp.read()
                if data[:5] == b"%PDF-":
                    extract_text(WORK / f"iclr{a.year % 100}-{pid}", data, titles[pid])
                    got.append(pid)
            except Exception as e:
                print(f"  arXiv failed {pid}: {e}", file=sys.stderr)
            time.sleep(3)
        else:
            by_batch.setdefault(s, set()).add(pid)
    for s, pids in sorted(by_batch.items()):
        repo, b = s.split("/batch_")
        url = f"{HF}{repo}/resolve/main/pdfs_batch_{b}.tar.gz"
        req = urllib.request.Request(url, headers={"User-Agent": "paper-review-eval/1.0"})
        left = set(pids)
        with urllib.request.urlopen(req, timeout=120) as resp, \
                tarfile.open(fileobj=resp, mode="r|gz") as tar:
            for m in tar:
                pid = Path(m.name).stem
                if m.isfile() and pid in left:
                    extract_text(WORK / f"iclr{a.year % 100}-{pid}",
                                 tar.extractfile(m).read(), titles[pid])
                    got.append(pid)
                    left.discard(pid)
                    if not left:
                        break
    print(f"{len(got)}/{len(rows)} selected papers fetched", file=sys.stderr)
    if a.ids_out:
        Path(a.ids_out).write_text(json.dumps([f"iclr{a.year % 100}-{p}" for p in got]))


# ---------- evaluate ----------

def solve(A, b):
    """Gaussian elimination with partial pivoting."""
    n = len(A)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        if abs(M[c][c]) < 1e-12:
            raise ValueError("singular system")
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                M[r] = [x - f * y for x, y in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


def fit_linear(X, y, ridge=1e-6):
    """OLS with intercept. A tiny ridge keeps constant columns (ethics is often 100
    everywhere) from making the system singular."""
    Z = [[1.0] + list(x) for x in X]
    k = len(Z[0])
    A = [[sum(z[i] * z[j] for z in Z) + (ridge if i == j and i else 0.0) for j in range(k)]
         for i in range(k)]
    b = [sum(z[i] * t for z, t in zip(Z, y)) for i in range(k)]
    return solve(A, b)


def predict(w, x):
    return w[0] + sum(wi * xi for wi, xi in zip(w[1:], x))


def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def pearson(x, y):
    mx, my = statistics.mean(x), statistics.mean(y)
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    sx = math.sqrt(sum((a - mx) ** 2 for a in x))
    sy = math.sqrt(sum((b - my) ** 2 for b in y))
    return sxy / (sx * sy) if sx and sy else float("nan")


def spearman(x, y):
    return pearson(ranks(x), ranks(y))


def auc(scores, labels):
    """Mann-Whitney AUC; ties count one half."""
    r = ranks(scores)
    npos = sum(labels)
    nneg = len(labels) - npos
    if not npos or not nneg:
        return float("nan")
    return (sum(ri for ri, l in zip(r, labels) if l) - npos * (npos + 1) / 2) / (npos * nneg)


def bootstrap(fn, n_items, reps=2000, seed=0):
    rng = random.Random(seed)
    vals = []
    for _ in range(reps):
        idx = [rng.randrange(n_items) for _ in range(n_items)]
        v = fn(idx)
        if not math.isnan(v):
            vals.append(v)
    if not vals:  # e.g. a constant score: Spearman is undefined in every resample
        return float("nan"), float("nan")
    vals.sort()
    return vals[int(0.025 * len(vals))], vals[int(0.975 * len(vals)) - 1]


def r3(x):
    """Round for the JSON report; undefined values become null."""
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(x, 3)


def nmae(pred, gt, lo, hi):
    """Normalized mean absolute error (CSPaper benchmark): mean |gt - pred| / (hi - lo),
    with lo and hi the venue's rating-scale bounds. Lower is better."""
    return statistics.mean(abs(g - p) for p, g in zip(pred, gt)) / (hi - lo)


def nme(pred, gt, lo, hi):
    """Normalized mean error (CSPaper benchmark): mean (pred - gt) / (hi - lo). Positive
    means the AI scores higher than the humans; zero is ideal."""
    return statistics.mean(p - g for p, g in zip(pred, gt)) / (hi - lo)


def error_metric(name, fn, pred, gt, idx_all, scale, reps):
    """NMAE/NME with the per-paper standard deviation (as CSPaper reports it) and a
    bootstrap 95% CI of the mean."""
    lo, hi = scale
    point = fn([pred[i] for i in idx_all], [gt[i] for i in idx_all], lo, hi)
    per = [fn([pred[i]], [gt[i]], lo, hi) for i in idx_all]
    clo, chi = bootstrap(lambda idx: fn([pred[idx_all[i]] for i in idx],
                                        [gt[idx_all[i]] for i in idx], lo, hi), len(idx_all), reps)
    return {"metric": name, "value": r3(point),
            "std": r3(statistics.pstdev(per)) if len(per) > 1 else 0.0,
            "ci95": [r3(clo), r3(chi)]}


SCALES = {2025: (1, 10), 2026: (0, 10)}  # ICLR overall rating bounds per year
# The skill's 1-6 Overall -> ICLR rating, from academic-paper-reviewer/scripts/venues.json
# ("map" for 2026, "legacy_map" for 2025). Interpolated linearly for panel means.
ICLR_MAPS = {2026: {1: 0, 2: 2, 3: 4, 4: 6, 5: 8, 6: 10},
             2025: {1: 1, 2: 3, 3: 5, 4: 6, 5: 8, 6: 10}}


def to_iclr(overall, year=2026):
    """Map a (possibly fractional) 1-6 Overall to the year's ICLR rating scale."""
    m = ICLR_MAPS[year]
    x = min(6.0, max(1.0, float(overall)))
    lo = min(int(x), 5)
    return m[lo] + (m[lo + 1] - m[lo]) * (x - lo)
WITHDRAWN = ("Withdrawn", "Desk rejected")


def evaluate(rows, feats, target="mean_human", reps=2000, low=5.0, scale=(0, 10)):
    rows = [r for r in rows if r["paper_id"] in feats]
    train = [r for r in rows if r["split"] == "train"]
    test = [r for r in rows if r["split"] == "test"]
    X = lambda rs: [[feats[r["paper_id"]][d] for d in DIMS] for r in rs]  # noqa: E731
    w = fit_linear(X(train), [r[target] for r in train])
    ai = [predict(w, x) for x in X(test)]
    one = [r["one_human"] for r in test]
    lab = [int(r["accepted"]) for r in test]
    mean = [r["mean_human"] for r in test]
    other = [r["other_human"] for r in test]

    def metric(name, fn, idx_all):
        point = fn(idx_all)
        lo, hi = bootstrap(lambda idx: fn([idx_all[i] for i in idx]), len(idx_all), reps)
        return {"metric": name, "value": round(point, 3), "ci95": [round(lo, 3), round(hi, 3)]}

    def report(idx):
        p = [i for i in idx if test[i]["other_human"] is not None]
        return {
            "n_test": len(idx), "n_accepted": sum(lab[i] for i in idx),
            "results": [
                metric("spearman(AI, one human)",
                       lambda I: spearman([ai[i] for i in I], [one[i] for i in I]), idx),
                metric("spearman(one human, another human)",
                       lambda I: spearman([one[i] for i in I],
                                          [test[i]["other_human"] for i in I]), p),
                metric("AUC(one human score -> accept)",
                       lambda I: auc([one[i] for i in I], [lab[i] for i in I]), idx),
                metric("AUC(AI score -> accept)",
                       lambda I: auc([ai[i] for i in I], [lab[i] for i in I]), idx),
            ],
            # CSPaper-style errors against the mean human rating, on the rating scale.
            # The AI score here is the regression output, so it is calibrated to that scale.
            "errors": [
                error_metric("NMAE(AI, mean human)", nmae, ai, mean, idx, scale, reps),
                error_metric("NME(AI, mean human)", nme, ai, mean, idx, scale, reps),
                error_metric("NMAE(one human, another human)", nmae, one, other, p, scale, reps),
            ],
            "calibration": calibration([test[i] for i in idx], [ai[i] for i in idx], low),
        }

    # Main protocol keeps withdrawn papers that have scores (as not accepted), like
    # paperreview.ai. They are easy negatives (authors usually withdraw after low scores),
    # so the harder subset without withdrawn and desk-rejected papers is reported too.
    # The regression is fitted once, on the full train split.
    allidx = list(range(len(test)))
    decided = [i for i in allidx if test[i].get("decision") not in WITHDRAWN]
    return {
        "n_train": len(train), "n_test": len(test),
        "weights": dict(zip(["intercept"] + DIMS, (round(x, 4) for x in w))),
        "all_scored": report(allidx),
        "without_withdrawn": report(decided),
        "reference_paperreview_ai": {"spearman_human_human": 0.41, "spearman_ai_human": 0.42,
                                     "auc_one_human": 0.84, "auc_ai": 0.75},
    }


def calibration(test, ai, low=5.0):
    """Share of test papers with an AI score at or below `low`, for each range of mean
    human score (the paperreview.ai calibration plot). paperreview.ai used 5.5 on the
    ICLR 2025 scale {1,3,5,6,8,10}; on the 2026 scale {0,2,4,6,8,10} the reject/accept
    boundary sits between 4 and 6, hence 5.0."""
    bins = [(0, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 11)]
    rows = []
    for lo, hi in bins:
        idx = [i for i, r in enumerate(test) if lo <= r["mean_human"] < hi]
        if idx:
            rows.append({"mean_human": f"[{lo},{hi})", "n": len(idx),
                         "share_ai_le_%s" % low: round(sum(ai[i] <= low for i in idx) / len(idx), 3)})
    return rows


def load_features(path):
    feats = {}
    for line in open(path):
        f = json.loads(line)
        if all(isinstance(f["dims"].get(d), (int, float)) for d in DIMS):
            feats[f["paper_id"]] = f["dims"]
    return feats


def venue_rating(res, venue="iclr"):
    """The skill's own (uncalibrated) overall rating on the venue's current scale, e.g. 4
    from the ICLR label "4 on {0,2,4,6,8,10} (5 on {1,3,5,6,8,10})"."""
    for v in res.get("venue_views") or []:
        if v.get("key") == venue:
            m = re.match(r"\s*(\d+(?:\.\d+)?)", str(v.get("label", "")))
            if m:
                return float(m.group(1))
    return None


def cmd_features(a):
    """Collect the 7 EIC-weighted dimension scores from each run's aggregate.json, plus
    the final 1-6 Overall and the skill's own ICLR-scale rating."""
    n = 0
    with open(a.out, "w") as out:
        for agg in sorted(Path(a.results).glob("*/aggregate.json")):
            try:
                res = json.loads(agg.read_text())
            except ValueError:
                continue
            dims = {d["key"]: d["weighted_avg"] for d in res.get("dimensions", [])}
            pid = agg.parent.name.split("-", 1)[-1]
            out.write(json.dumps({"paper_id": pid, "dims": dims,
                                  "overall": res.get("final_overall"),
                                  "official_rating": res.get("official_rating"),
                                  "rating": venue_rating(res)}) + "\n")
            n += 1
    print(f"{n} runs with aggregate.json", file=sys.stderr)


def load_ratings(path):
    out = {}
    for line in open(path):
        f = json.loads(line)
        out[f["paper_id"]] = f
    return out


def pilot(rows, feats, reps=2000, scale=(0, 10), year=2026):
    """Metrics without a train/test split, for pilots too small to fit the regression.
    Uses the skill's own outputs as they are, never fitted to the human scores:
    - panel rating: the reviewers' mean 1-6 Overall ("official_rating"), mapped to the ICLR
      scale. It is a mean of reviewers, like the mean human rating it is compared with.
    - ICLR-scale rating: the skill's final (integer) rating on the ICLR scale.
    Errors are CSPaper-style NMAE/NME against the mean human rating."""
    rows = [r for r in rows if r["paper_id"] in feats]
    lab = [int(r["accepted"]) for r in rows]
    mean = [r["mean_human"] for r in rows]
    out = {"n": len(rows), "n_accepted": sum(lab), "scale": list(scale), "results": []}
    allidx = list(range(len(rows)))

    def num(x):
        return float(x) if isinstance(x, (int, float)) else None

    preds = {
        "panel rating": [None if num(feats[r["paper_id"]].get("official_rating")) is None
                         else to_iclr(feats[r["paper_id"]]["official_rating"], year)
                         for r in rows],
        "ICLR-scale rating": [num(feats[r["paper_id"]].get("rating")) for r in rows],
    }
    for label, v in preds.items():
        idx = [i for i in allidx if v[i] is not None]
        if len(idx) < 3:
            continue
        sp = spearman([v[i] for i in idx], [mean[i] for i in idx])
        lo, hi = bootstrap(lambda I: spearman([v[idx[i]] for i in I],
                                              [mean[idx[i]] for i in I]), len(idx), reps)
        out["results"] += [
            {"metric": f"spearman({label}, mean human)", "value": r3(sp), "ci95": [r3(lo), r3(hi)]},
            {"metric": f"AUC({label} -> accept)",
             "value": r3(auc([v[i] for i in idx], [lab[i] for i in idx]))},
            error_metric(f"NMAE({label}, mean human)", nmae, v, mean, idx, scale, reps),
            error_metric(f"NME({label}, mean human)", nme, v, mean, idx, scale, reps)]
    one = [r["one_human"] for r in rows]
    other = [r["other_human"] for r in rows]
    p = [i for i in allidx if other[i] is not None]
    const = [statistics.median(mean)] * len(rows)
    out["reference"] = [
        error_metric("NMAE(one human, another human)", nmae, one, other, p, scale, reps),
        error_metric("NMAE(one human, mean human)", nmae, one, mean, allidx, scale, reps),
        # A constant at the median of these papers' own mean ratings (an oracle constant):
        # NMAE rewards predicting the middle, so a useful system should beat this.
        error_metric("NMAE(constant median, mean human)", nmae, const, mean, allidx, scale, reps),
        {"metric": "spearman(one human, another human)",
         "value": r3(spearman([one[i] for i in p], [other[i] for i in p]))},
        {"metric": "AUC(one human -> accept)", "value": r3(auc(one, lab))}]
    return out


def cmd_pilot(a):
    rows = [json.loads(l) for l in open(a.sample)]
    if a.ids:
        keep = set(json.load(open(a.ids)))
        rows = [r for r in rows if r["paper_id"] in keep]
    print(json.dumps(pilot(rows, load_ratings(a.features), reps=a.reps, year=a.year,
                           scale=tuple(a.scale) if a.scale else SCALES[a.year]), indent=2))


def cmd_evaluate(a):
    rows = [json.loads(l) for l in open(a.sample)]
    if a.splits:  # the balanced split written by fetch --splits-out
        sp = json.load(open(a.splits))
        rows = [dict(r, split=sp[r["paper_id"]]) for r in rows if r["paper_id"] in sp]
    res = evaluate(rows, load_features(a.features), reps=a.reps, low=a.low,
                   scale=tuple(a.scale) if a.scale else SCALES[a.year])
    print(json.dumps(res, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample")
    s.add_argument("parquet")
    s.add_argument("--year", type=int, default=2026)
    s.add_argument("--source", choices=["jerma", "berens"], default="jerma")
    s.add_argument("--n", type=int, default=300)
    s.add_argument("--train", type=int, default=150)
    s.add_argument("--seed", type=int, default=2025)
    s.add_argument("--out", required=True)
    f = sub.add_parser("find")
    f.add_argument("sample")
    f.add_argument("--year", type=int, default=2026)
    f.add_argument("--decision-date", help="default: the year's ICLR decision date")
    f.add_argument("--split", choices=["all", "train", "test"], default="all")
    f.add_argument("--offset", type=int, default=0)
    f.add_argument("--limit", type=int, default=0)
    f.add_argument("--openreview", action="store_true", help="fall back to OpenReview PDFs")
    f.add_argument("--ids-out", help="write the ids that have text, as a JSON list")
    q = sub.add_parser("pdfs", help="stream paperreview.ai's ICLR 2026 PDF dump")
    q.add_argument("sample")
    q.add_argument("--year", type=int, default=2026)
    q.add_argument("--batches", type=int, nargs="*", help="batch numbers (default: all 40)")
    o = sub.add_parser("sources", help="write the committed map of text sources")
    o.add_argument("sample")
    o.add_argument("--year", type=int, default=2026)
    o.add_argument("--out", required=True)
    o.add_argument("--decision-date", help="default: the year's ICLR decision date")
    o.add_argument("--dump", action="store_true",
                   help="also use paperreview.ai dump PDFs. Off by default: the dump has "
                        "camera-ready PDFs for accepted papers and anonymous submissions for "
                        "the rest, a decision cue that normalization cannot remove")
    h = sub.add_parser("fetch", help="download text for selected rows from the source map")
    h.add_argument("sample")
    h.add_argument("sources")
    h.add_argument("--year", type=int, default=2026)
    h.add_argument("--split", choices=["all", "train", "test"], default="all")
    h.add_argument("--offset", type=int, default=0)
    h.add_argument("--limit", type=int, default=0)
    h.add_argument("--ids-out")
    h.add_argument("--splits-out", help="with --pick balanced/stratified: write the balanced split")
    h.add_argument("--dry-run", action="store_true", help="select only; no downloads")
    h.add_argument("--prefer", help="JSON list of paper ids to prefer in the pick "
                                    "(e.g. an earlier pilot, for a like-for-like rerun)")
    h.add_argument("--reviewed", help="JSON list of paper ids already reviewed: kept in the "
                                      "balanced set (preferred) and not fetched again")
    h.add_argument("--pick", choices=["order", "stratified", "balanced"], default="order",
                   help="stratified: decision mix of the whole sample, spread over scores, "
                        "areas and sources (for pilots); balanced: per split, the largest "
                        "subset with the whole split's decision mix (for the full run)")
    g = sub.add_parser("features")
    g.add_argument("results", help="directory of <id>/aggregate.json runs")
    g.add_argument("--out", required=True)
    e = sub.add_parser("evaluate")
    e.add_argument("sample")
    e.add_argument("features")
    e.add_argument("--reps", type=int, default=2000)
    e.add_argument("--splits", help="JSON {paper_id: train|test} from fetch --splits-out")
    e.add_argument("--low", type=float, default=5.0,
                   help="AI-score threshold for the calibration table (5.5 for ICLR 2025)")
    for sp in (e, sub.add_parser("pilot", help="metrics on all reviewed papers, no "
                                 "regression: the skill's own ratings vs the mean human")):
        sp.add_argument("--year", type=int, default=2026,
                        help="sets the rating scale for NMAE/NME (2025: 1-10, 2026: 0-10)")
        sp.add_argument("--scale", type=float, nargs=2, metavar=("MIN", "MAX"),
                        help="rating-scale bounds for NMAE/NME (overrides --year)")
    pl = sub.choices["pilot"]
    pl.add_argument("sample")
    pl.add_argument("features")
    pl.add_argument("--ids", help="JSON list of paper ids to include (default: all with features)")
    pl.add_argument("--reps", type=int, default=2000)
    a = ap.parse_args()
    {"sample": cmd_sample, "find": cmd_find, "pdfs": cmd_pdfs, "sources": cmd_sources,
     "fetch": cmd_fetch, "features": cmd_features,
     "evaluate": cmd_evaluate, "pilot": cmd_pilot}[a.cmd](a)


if __name__ == "__main__":
    main()
