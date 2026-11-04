#!/usr/bin/env python3
"""Review-diversity audit (after ScholarPeer's Review Diversity Score).

    python3 evals/audit_diversity.py evals/manifest_lit27.json [more manifests ...]

Two numbers per run, both 1 - mean pairwise TF-IDF cosine (standard library):
  * panel diversity: between the five Phase 1 reports in one review.md
    (do the five roles actually say different things, or one opinion five times?)
  * rerun diversity: between full reviews of the same paper across skill
    versions/runs (base_id), when several exist
Higher is more diverse. Reports are split on their ### headings (Report N, Review N, Reviewer N, Devil's Advocate).
"""

import importlib.util
import itertools
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work" / "results"
spec = importlib.util.spec_from_file_location(
    "rs", ROOT.parent / "academic-paper-reviewer" / "scripts" / "related_search.py")
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)


def pairwise_diversity(texts):
    if len(texts) < 2:
        return None
    sims = []
    for i, j in itertools.combinations(range(len(texts)), 2):
        sims.append(rs.tfidf_cosines(texts[i], [texts[j]])[0])
    return round(1 - sum(sims) / len(sims), 3)


HEAD = re.compile(r"^###\s+(?:(?:Report|Review|Reviewer)\s+\d|Devil'?s Advocate)", re.M | re.I)
END = re.compile(r"^##\s+(Phase\s+1\.5|Phase\s+2|Literature|Consensus|EIC|Editorial)", re.M | re.I)


def reports(review):
    """The five Phase 1 reports, split on their ### headings (formats vary between runs)."""
    starts = [m.start() for m in HEAD.finditer(review)][:5]
    if len(starts) < 2:
        return []
    stop = END.search(review, starts[-1])
    bounds = starts + [stop.start() if stop else len(review)]
    return [review[a:b] for a, b in zip(bounds, bounds[1:])]


def main():
    rows = []
    for mpath in sys.argv[1:]:
        for p in json.load(open(mpath)):
            f = WORK / p["id"] / "review.md"
            if not f.exists():
                continue
            reps = reports(f.read_text(errors="replace"))
            rows.append({"id": p["id"], "base": p["base_id"], "n_reports": len(reps),
                         "panel_diversity": pairwise_diversity(reps)})
    out = ["# Review diversity", "", "1 − mean pairwise TF-IDF cosine. Higher = more diverse.", "",
           "| Run | Reports found | Panel diversity |", "|---|---|---|"]
    out += [f"| {r['id']} | {r['n_reports']} | {r['panel_diversity']} |" for r in rows]
    by_base = {}
    for r in rows:
        by_base.setdefault(r["base"], []).append(r["id"])
    rerun = []
    for base, ids in by_base.items():
        texts = [(WORK / i / "review.md").read_text(errors="replace") for i in ids]
        if len(texts) > 1:
            rerun.append((base, len(ids), pairwise_diversity(texts)))
    if rerun:
        out += ["", "| Paper | Runs | Rerun diversity |", "|---|---|---|"]
        out += [f"| {b} | {n} | {d} |" for b, n, d in rerun]
    vals = [r["panel_diversity"] for r in rows if r["panel_diversity"] is not None]
    if vals:
        out += ["", f"Mean panel diversity: {sum(vals) / len(vals):.3f} over {len(vals)} runs"]
    print("\n".join(out))


if __name__ == "__main__":
    main()
