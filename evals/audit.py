#!/usr/bin/env python3
"""Audit skill outputs produced by evals/review_prompt.md runs.

    python3 evals/audit.py evals/manifest.json [--check-refs]

Reads evals/work/results/<id>/ and evals/work/papers/<id>/paper.txt and writes
  evals/REPORT.md               aggregate metrics (safe to commit)
  evals/work/report_detail.md   per-paper table and every failed check

Checks per paper:
  * structure    required files and sections are present, JSON parses
  * locations    every cited Table/Figure/Section/Equation exists in the paper
  * quotes       every quoted phrase appears in the paper (exact or near-exact)
  * numbers      every quoted number appears in the paper
  * references   (with --check-refs) recommended references found on arXiv by title
  * decision     final Overall, venue label, DA-CRITICAL rates, consistency warnings
"""

import argparse
import difflib
import json
import re
import statistics
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
SECTIONS = [
    ("phase0", r"paper analysis|reviewer configuration|review team"),
    ("eic", r"editor-in-chief|\beic\b"),
    ("r1", r"methodology"),
    ("r2", r"domain"),
    ("r3", r"perspective"),
    ("da", r"devil'?s advocate"),
    ("decision", r"editorial decision"),
    ("roadmap", r"revision roadmap"),
]


def norm(text):
    text = text.replace("­", "").replace("ﬁ", "fi").replace("ﬂ", "fl")
    text = re.sub(r"-\s*\n\s*", "", text)          # de-hyphenate line breaks
    text = re.sub(r"[‘’]", "'", text)
    text = re.sub(r"[“”]", '"', text)
    text = re.sub(r"[–—]", "-", text)
    return re.sub(r"\s+", " ", text).lower().strip()


def location_exists(loc, raw, flat):
    m = re.match(r"\s*(table|tab\.?|figure|fig\.?|section|sec\.?|§|appendix|app\.?|"
                 r"equation|eq\.?|eqn\.?|algorithm|alg\.?)\s*([A-Z]?\d+(?:\.\d+)*|[A-Z])\b",
                 loc, re.I)
    if not m:
        return None  # unrecognized format: not checked
    kind, num = m.group(1).lower().rstrip("."), m.group(2)
    n = re.escape(num)
    if kind.startswith(("tab",)):
        pats = [rf"\btab(le|\.)?\s*{n}\b"]
    elif kind.startswith("fig"):
        pats = [rf"\bfig(ure|\.)?\s*{n}\b"]
    elif kind.startswith(("sec", "§")):
        # two-column layouts put headings mid-line, so allow a wide gap before them
        pats = [rf"\bsec(tion|\.)?\s*{n}\b", rf"§\s*{n}\b", rf"(^|\s{{2,}}|\n)\s*{n}\.?\s+[A-Z][a-z]"]
    elif kind.startswith("app"):
        pats = [rf"\bappendix\s*{n}\b", rf"(^|\n)\s*{n}(\.\d+)*\.?\s+[A-Z]"]
    elif kind.startswith("alg"):
        pats = [rf"\balgorithm\s*{n}\b"]
    else:
        pats = [rf"\(\s*{n}\s*\)", rf"\beq(uation|n?\.)?\s*\(?{n}\)?"]
    return any(re.search(p, raw, re.I | re.M) for p in pats)


def quote_found(q, flat):
    nq = norm(q).strip(" .\"'")
    if len(nq) < 8:
        return None
    if nq in flat:
        return "exact"
    sm = difflib.SequenceMatcher(None, flat, nq, autojunk=False)
    m = sm.find_longest_match(0, len(flat), 0, len(nq))
    if m.size / len(nq) >= 0.85:
        return "near"
    # windowed fuzzy match around the best anchor
    start = max(0, m.a - m.b - 20)
    window = flat[start:start + len(nq) + 40]
    if difflib.SequenceMatcher(None, window, nq).ratio() >= 0.85:
        return "near"
    return "missing"


def number_found(value, flat):
    """True if every number in `value` appears in the paper ("32.0 / 29.8" checks both)."""
    v = str(value).lower().replace(",", "")
    if re.search(r"\d\s*e\s*-?\d", v):      # scientific notation is printed differently
        return None
    tokens = re.findall(r"\d+(?:\.\d+)?", v)
    if not tokens:
        return None
    text = flat.replace(",", "")
    return all(re.search(rf"(?<![\d.]){re.escape(t)}(?![\d])", text) for t in tokens)


def arxiv_has_title(title):
    stop = {"a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "into",
            "is", "it", "of", "on", "or", "the", "to", "via", "with", "without", "towards"}
    words = [w for w in re.findall(r"[A-Za-z0-9]+", title) if w.lower() not in stop and len(w) > 1]
    if len(words) < 3:
        return None
    q = " AND ".join(f"ti:{w}" for w in dict.fromkeys(words[:8]))
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(
        {"search_query": q, "max_results": 5})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                body = r.read().decode("utf-8", "replace")
            break
        except Exception:
            time.sleep(5 * 2 ** attempt)
    else:
        return None
    found = re.findall(r"<entry>.*?<title>(.*?)</title>", body, re.S)
    target = norm(title)
    return any(difflib.SequenceMatcher(None, norm(t), target).ratio() >= 0.85 for t in found)


def load(path):
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def audit_paper(p, check_refs):
    rid = p["id"]
    rdir = WORK / "results" / rid
    raw = (WORK / "papers" / rid / "paper.txt").read_text(errors="replace")
    flat = norm(raw)
    res = {"id": rid, "venue": p["venue"], "topic": p["topic"], "title": p["title"],
           "planted": p.get("planted_flaw", ""), "problems": []}
    review = (rdir / "review.md").read_text(errors="replace") if (rdir / "review.md").exists() else ""
    summary, scores, agg, ev = (load(rdir / f) for f in
                                ("summary.json", "scores.json", "aggregate.json", "evidence.json"))
    res["complete"] = all(x is not None for x in (summary, scores, agg, ev)) and bool(review)
    if not res["complete"]:
        res["problems"].append("missing or invalid output files")
        return res
    res["words"] = len(review.split())
    low = review.lower()
    res["missing_sections"] = [n for n, pat in SECTIONS if not re.search(pat, low)]

    res["final"] = summary.get("final_overall")
    res["label"] = summary.get("venue_recommendation")
    res["composite"] = agg.get("panel_composite")
    res["composite_band"] = agg.get("suggested_overall")
    res["ceiling"] = agg.get("final_overall_ceiling")
    res["warnings"] = len(agg.get("warnings", []))
    res["da_raised"] = summary.get("da_critical_raised", 0) or 0
    res["da_upheld"] = summary.get("da_critical_upheld", 0) or 0
    res["recognized"] = bool(summary.get("recognized"))
    res["injection"] = summary.get("injection_found")
    res["paper_type"] = summary.get("paper_type")
    before = load(rdir / "before.json")
    res["before_composite"] = before.get("before_composite", before.get("panel_composite")) if before else summary.get("before_composite")
    res["after_composite"] = agg.get("panel_composite")
    res["eic_weights"] = [r.get("eic_weight") for r in scores.get("reviewers", [])]
    if p.get("planted_flaw"):
        key = {"test-tuning": r"(tun|select)\w*[^.]{0,80}test set|test[- ]set[^.]{0,40}(tun|select)",
               "train-on-test": r"(merg|train)\w*[^.]{0,80}test (split|set)|test (split|set)[^.]{0,60}(train|merg)"}[p["planted_flaw"]]
        da = re.search(r"critical issues(.*?)(major issues|$)", low, re.S)
        res["flaw_mentioned"] = bool(re.search(key, low))
        res["flaw_in_da_critical"] = bool(da and re.search(key, da.group(1)))
    res["overalls"] = [r.get("overall") for r in scores.get("reviewers", [])]
    if isinstance(res["final"], int) and isinstance(res["ceiling"], int) and res["final"] > res["ceiling"]:
        res["problems"].append(f"final {res['final']} exceeds ceiling {res['ceiling']}")

    locs = sorted(set(ev.get("locations", [])))
    checked = [(l, location_exists(l, raw, flat)) for l in locs]
    res["loc_total"] = sum(1 for _, ok in checked if ok is not None)
    res["loc_bad"] = [l for l, ok in checked if ok is False]

    quotes = ev.get("quotes", [])
    qres = [(q, quote_found(q, flat)) for q in quotes]
    res["quote_total"] = sum(1 for _, r in qres if r)
    res["quote_bad"] = [q for q, r in qres if r == "missing"]

    nums = [n for n in ev.get("numbers", []) if isinstance(n, dict)]
    derived_pat = re.compile(r"recomput|computed|derived|mean of|average of|plain mean|"
                             r"\bgain\b|\bdelta\b|difference|implied", re.I)
    is_derived = lambda n: n.get("derived") or derived_pat.search(str(n.get("claim", "")))
    res["num_derived"] = sum(1 for n in nums if is_derived(n))
    nres = [(n, number_found(n.get("value", ""), flat)) for n in nums if not is_derived(n)]
    res["num_total"] = sum(1 for _, r in nres if r is not None)
    res["num_bad"] = [f"{n.get('claim')}: {n.get('value')}" for n, r in nres if r is False]

    refs = ev.get("references", [])
    res["ref_total"] = len(refs)
    res["ref_verify_marked"] = sum(1 for r in refs if r.get("marked_verify"))
    if check_refs:
        res["ref_not_found"] = []
        for r in refs:
            if r.get("marked_verify") or not r.get("title"):
                continue
            ok = arxiv_has_title(r["title"])
            time.sleep(3)
            if ok is False:
                res["ref_not_found"].append(f"{r.get('title')} ({r.get('authors', '?')}, {r.get('year', '?')})")
        res["ref_checked"] = sum(1 for r in refs if not r.get("marked_verify") and r.get("title"))
    return res


def pct(a, b):
    return f"{100 * a / b:.0f}%" if b else "n/a"


def wilson(k, n, z=1.96):
    if not n:
        return (0, 0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return (max(0, c - h), min(1, c + h))


def report(results, check_refs):
    controls = [r for r in results if r.get("complete") and "flaw_mentioned" in r]
    results = [r for r in results if "flaw_mentioned" not in r and not r["id"].endswith("-flaw")]
    done = [r for r in results if r.get("complete")]
    n = len(done)
    lines = ["# Evaluation Report: Recently Accepted Papers", "",
             f"Papers sampled: {len(results)} · complete runs: {n}", ""]
    if not n:
        return "\n".join(lines), ""
    finals = [r["final"] for r in done if isinstance(r["final"], int)]
    acc = sum(1 for f in finals if f >= 4)
    lo, hi = wilson(acc, len(finals))
    dist = Counter(finals)
    lines += [
        "## Decisions (reference only)", "",
        "All sampled papers were accepted at their venue. Agreement with that outcome is reported **for reference, "
        "not as a target**: the skill is not tuned to reproduce venue decisions. The primary checks are grounding, "
        "the planted-flaw controls and internal consistency (below).", "",
        f"- Accept-side (Overall ≥ 4): **{acc}/{len(finals)} = {pct(acc, len(finals))}** (95% CI {lo:.0%}–{hi:.0%})",
        f"- Overall distribution: " + ", ".join(f"{k}: {dist.get(k, 0)}" for k in range(6, 0, -1)),
        f"- Mean Overall: {statistics.mean(finals):.2f}; mean panel composite: "
        f"{statistics.mean(r['composite'] for r in done if r['composite'] is not None):.1f}",
        "",
        "| Slice | n | Accept-side | Mean Overall |",
        "|---|---|---|---|",
    ]
    for key in ("venue", "topic"):
        groups = defaultdict(list)
        for r in done:
            groups[r[key]].append(r)
        for g, rs in sorted(groups.items()):
            fs = [r["final"] for r in rs if isinstance(r["final"], int)]
            k = sum(1 for f in fs if f >= 4)
            lines.append(f"| {key}: {g} | {len(fs)} | {k}/{len(fs)} | {statistics.mean(fs):.2f} |")
    bc = [r["before_composite"] for r in done if isinstance(r.get("before_composite"), (int, float))]
    ac = [r["after_composite"] for r in done if isinstance(r.get("after_composite"), (int, float))]
    if bc and ac:
        lines += ["", "## BEFORE vs AFTER (EIC weighting)", "",
                  f"- Mean composite BEFORE (confidence-weighted): {statistics.mean(bc):.1f}",
                  f"- Mean composite AFTER (EIC-weighted): {statistics.mean(ac):.1f}",
                  f"- Mean |AFTER − BEFORE|: {statistics.mean(abs(r['after_composite'] - r['before_composite']) for r in done if isinstance(r.get('before_composite'), (int, float))):.1f}",
                  f"- Decisions departing from the AFTER band: "
                  f"{sum(1 for r in done if r['final'] != r['composite_band'])}/{n}",
                  f"- Reviewers weighted ≠ 1.0 by the EIC: "
                  f"{sum(1 for r in done for w in r['eic_weights'] if w not in (None, 1, 1.0))}"
                  f"/{sum(len(r['eic_weights']) for r in done)}"]
    da_r = sum(1 for r in done if r["da_raised"])
    da_u = sum(1 for r in done if r["da_upheld"])
    capped = sum(1 for r in done if r["ceiling"] is not None and r["composite_band"] is not None
                 and r["ceiling"] < r["composite_band"])
    lines += ["", "## Devil's Advocate and decision mechanics", "",
              f"- Papers with ≥ 1 DA-CRITICAL raised: {da_r}/{n} ({pct(da_r, n)}); upheld: {da_u}/{n} ({pct(da_u, n)})",
              f"- Decisions lowered by the DA cap: {capped}/{n}",
              f"- Papers with consistency warnings: {sum(1 for r in done if r['warnings'])}/{n}",
              f"- Final exceeding the ceiling (rule violation): {sum(1 for r in done if any('exceeds ceiling' in p for p in r['problems']))}",
              f"- Papers the reviewer recognized from prior knowledge: {sum(r['recognized'] for r in done)}/{n}",
              f"- Prompt injections found in papers: {sum(1 for r in done if r['injection'])}",
              ""]
    lt = sum(r["loc_total"] for r in done); lb = sum(len(r["loc_bad"]) for r in done)
    qt = sum(r["quote_total"] for r in done); qb = sum(len(r["quote_bad"]) for r in done)
    nt = sum(r["num_total"] for r in done); nb = sum(len(r["num_bad"]) for r in done)
    lines += ["## Grounding (hallucination checks)", "",
              "| Check | Checked | Not found in paper | Rate |", "|---|---|---|---|",
              f"| Cited locations (tables, figures, sections, equations) | {lt} | {lb} | {pct(lb, lt)} |",
              f"| Quoted phrases | {qt} | {qb} | {pct(qb, qt)} |",
              f"| Quoted numbers | {nt} | {nb} | {pct(nb, nt)} |"]
    nd = sum(r.get("num_derived", 0) for r in done)
    lines.append(f"\nNumbers the reviewers recomputed themselves (excluded above; spot-checked by hand): {nd}.")
    rt = sum(r["ref_total"] for r in done)
    rv = sum(r["ref_verify_marked"] for r in done)
    if check_refs:
        rc = sum(r.get("ref_checked", 0) for r in done)
        rn = sum(len(r.get("ref_not_found", [])) for r in done)
        lines.append(f"| Recommended references (not marked `[verify]`) found on arXiv by title | {rc} | {rn} | {pct(rn, rc)} |")
    lines += ["", f"Recommended references: {rt} total, {rv} marked `[verify]`. "
              "A reference missing from arXiv is not necessarily fabricated (not every paper is on arXiv); "
              "those are listed in the detail file for manual checking.", "",
              "## Structure", "",
              f"- Runs with all required sections: {sum(1 for r in done if not r['missing_sections'])}/{n}",
              f"- Median review length: {statistics.median(r['words'] for r in done):.0f} words", ""]

    if controls:
        caught = sum(1 for r in controls if r["flaw_mentioned"])
        crit = sum(1 for r in controls if r["flaw_in_da_critical"])
        low_ = sum(1 for r in controls if isinstance(r["final"], int) and r["final"] <= 3)
        lines += ["## Planted-flaw controls", "",
                  "Accepted papers with one inserted sentence admitting a fatal evaluation flaw "
                  "(hyperparameters tuned on the test set, or test split merged into training). "
                  "A calibrated reviewer must catch it and decide ≤ 3.", "",
                  f"- Flaw mentioned in the review: {caught}/{len(controls)}",
                  f"- Flaw raised as DA-CRITICAL: {crit}/{len(controls)}",
                  f"- Decision ≤ 3: {low_}/{len(controls)}",
                  "", "| Control | Flaw | Mentioned | DA-CRITICAL | Final |", "|---|---|---|---|---|"]
        for r in controls:
            lines.append(f"| {r['venue']}-{r['topic']} | {r.get('planted', '')} | "
                         f"{'yes' if r['flaw_mentioned'] else 'NO'} | "
                         f"{'yes' if r['flaw_in_da_critical'] else 'no'} | {r['final']} |")
        lines.append("")
    det = ["# Per-paper detail (not for publication)", "",
           "| id | Final | Venue label | Composite | Reviewer Overalls | DA raised/upheld | Bad loc/quote/num |",
           "|---|---|---|---|---|---|---|"]
    for r in results:
        if not r.get("complete"):
            det.append(f"| {r['id']} | — | incomplete | | | | |")
            continue
        det.append(f"| {r['id']} | {r['final']} | {r['label']} | {r['composite']} | {r['overalls']} | "
                   f"{r['da_raised']}/{r['da_upheld']} | {len(r['loc_bad'])}/{len(r['quote_bad'])}/{len(r['num_bad'])} |")
    det.append("")
    for r in results:
        issues = r.get("problems", []) + [f"location not found: {x}" for x in r.get("loc_bad", [])] \
            + [f"quote not found: {x}" for x in r.get("quote_bad", [])] \
            + [f"number not found: {x}" for x in r.get("num_bad", [])] \
            + [f"reference not on arXiv: {x}" for x in r.get("ref_not_found", [])] \
            + [f"missing section: {x}" for x in r.get("missing_sections", [])]
        if r.get("injection"):
            issues.append(f"injection: {r['injection']}")
        if issues:
            det.append(f"## {r['id']}")
            det += [f"- {i}" for i in issues]
            det.append("")
    return "\n".join(lines), "\n".join(det)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("manifest", nargs="+", help="manifest(s), e.g. evals/manifest.json evals/manifest_controls.json")
    ap.add_argument("--check-refs", action="store_true")
    args = ap.parse_args()
    manifest = [p for m in args.manifest for p in json.load(open(m))]
    results = [audit_paper(p, args.check_refs) for p in manifest
               if (WORK / "results" / p["id"]).exists()]
    summary, detail = report(results, args.check_refs)
    (ROOT / "REPORT.md").write_text(summary + "\n")
    (WORK / "report_detail.md").write_text(detail + "\n")
    print(summary)


if __name__ == "__main__":
    main()
