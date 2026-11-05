#!/usr/bin/env python3
"""Build the ICLR 2026 calibration index from a public OpenReview dump.

    pip install pyarrow   # only this eval script needs it, not the skill
    python3 -I evals/iclr_benchmark.py evals/work/benchmarks/iclr2026/jerma.parquet \
        [--arxiv evals/work/benchmarks/iclr2026/aiconf.parquet] \
        --out evals/work/benchmarks/iclr2026/index.jsonl

Source: Hugging Face dataset JerMa88/ICLR_Peer_Reviews_2026. It has one row per human
OpenReview review, with rating, confidence and the final decision for accepted and
rejected submissions. The optional --arxiv file (ai-conferences/ICLR2026) adds arXiv
IDs for accepted papers.

The index is ground truth for calibration: human ratings and decisions. It lives
under evals/work/ (git-ignored) and must never be shown to the reviewer agents.
They get the paper text only. Output: one JSON object per submission with
paper_id, title, decision, accepted, oral, primary_area, ratings, confidences,
mean_rating, n_reviews, arxiv_id and forum URL.
"""

import argparse
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path


def load_rows(path):
    import pyarrow.parquet as pq
    cols = ["paper_id", "title", "decision", "rating", "confidence", "reviewer_id",
            "review_src", "api_raw_submission"]
    return pq.read_table(path, columns=cols).to_pydict()


def primary_area(raw):
    try:
        content = json.loads(raw).get("content", {})
    except (TypeError, ValueError):
        return None
    area = content.get("primary_area", {})
    return area.get("value") if isinstance(area, dict) else area


def build(rows, arxiv_by_id=None):
    papers = defaultdict(lambda: {"ratings": [], "confidences": [], "reviewers": set()})
    for i, pid in enumerate(rows["paper_id"]):
        if rows["review_src"][i] != "openreview":
            continue
        p = papers[pid]
        rid = rows["reviewer_id"][i]
        if rid in p["reviewers"]:
            continue  # one rating per reviewer
        p["reviewers"].add(rid)
        p.setdefault("title", rows["title"][i])
        p.setdefault("decision", rows["decision"][i])
        if "primary_area" not in p:
            p["primary_area"] = primary_area(rows["api_raw_submission"][i])
        if rows["rating"][i] is not None:
            p["ratings"].append(rows["rating"][i])
            p["confidences"].append(rows["confidence"][i])
    out = []
    for pid, p in papers.items():
        dec = p.get("decision") or "Unknown"
        if dec == "Unknown" or not p["ratings"]:
            continue  # withdrawn or no public ratings: no ground truth
        out.append({
            "paper_id": pid, "title": p.get("title"), "decision": dec,
            "accepted": dec.startswith(("Accept", "Conditional Accept")),
            "oral": "Oral" in dec, "primary_area": p.get("primary_area"),
            "ratings": p["ratings"], "confidences": p["confidences"],
            "mean_rating": round(statistics.mean(p["ratings"]), 3), "n_reviews": len(p["ratings"]),
            "arxiv_id": (arxiv_by_id or {}).get(pid),
            "forum": f"https://openreview.net/forum?id={pid}",
        })
    return sorted(out, key=lambda r: r["paper_id"])


def load_arxiv(path):
    import pyarrow.parquet as pq
    t = pq.read_table(path, columns=["paper_id", "arxiv_id"]).to_pydict()
    return {p: a for p, a in zip(t["paper_id"], t["arxiv_id"]) if a and a != "None"}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("reviews")
    ap.add_argument("--arxiv")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    index = build(load_rows(a.reviews), load_arxiv(a.arxiv) if a.arxiv else None)
    Path(a.out).write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in index))
    acc = [r for r in index if r["accepted"]]
    print(f"{len(index)} submissions with decisions and ratings: {len(acc)} accepted "
          f"({sum(r['oral'] for r in acc)} oral), {len(index) - len(acc)} rejected; "
          f"{sum(1 for r in index if r['arxiv_id'])} with an arXiv ID", file=sys.stderr)


if __name__ == "__main__":
    main()
