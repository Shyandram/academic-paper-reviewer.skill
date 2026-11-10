#!/usr/bin/env python3
"""Compare a small validation run with an earlier run of the same papers (numbers and IDs only).

    python3 evals/validation_compare.py NEW_DIR OLD_DIR [--prices 1,0.05,5] [--label ...] > out.json

NEW_DIR and OLD_DIR are gitignored per-paper result directories under evals/work/
(iclr26-<id>/...). The human mean rating comes from evals/work/sol_metrics/sample.jsonl
when present; it is used here only for the comparison, never by a review job. The
novelty profile is re-read with the current scripts/related_search.py. Prices are USD
per 1M tokens (fresh input, cached input, output) for the cost column. Stdlib only.
"""
import argparse
import json
import os
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "academic-paper-reviewer", "scripts"))
import related_search as rs  # noqa: E402


def load(p):
    try:
        with open(p) as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def paper(d, prices):
    s = load(os.path.join(d, "summary.json")) or {}
    sc = load(os.path.join(d, "scores.json")) or {}
    run = load(os.path.join(d, "run.json")) or {}
    pools = [r.get("pool_position") for r in sc.get("reviewers", [])]
    out = {"reviewer_pools": pools,
           "reviewer_pool_mean": round(st.mean(p for p in pools if p is not None), 1) if any(
               p is not None for p in pools) else None,
           "official_rating": s.get("official_rating"), "eic_pool": s.get("eic_pool_position"),
           "final_overall": s.get("final_overall")}
    prof = load(os.path.join(d, "novelty_profile.json"))
    if prof:
        try:
            n = rs.novelty_profile(prof)
            out["novelty"] = {"verdicts": [c["verdict"] if c["verdict"] in rs.CONTRIBUTION_BAND else "none found"
                                           for c in n["claims"] if c["central"]],
                              "paper_novelty": n["paper_novelty"], "primary": n.get("primary")}
        except ValueError as e:
            out["novelty"] = {"error": str(e)[:200]}
    rv = os.path.join(d, "review.md")
    if os.path.exists(rv):
        t = open(rv, errors="replace").read()
        out["markers"] = {k: len(re.findall(p, t, re.I)) for k, p in [
            ("contribution_position", r"contribution position"), ("evidence_adjustment", r"evidence adjustment"),
            ("case_for_acceptance", r"(case for acceptance|acceptance case)"),
            ("repair_test", r"\b(intact|weakened|lost)\b")]}
    u = run.get("usage") or {}
    if u:
        fresh = u.get("input_tokens", 0) - u.get("cached_input_tokens", 0)
        out["tokens"] = {k: u.get(k) for k in ("input_tokens", "cached_input_tokens", "output_tokens",
                                               "reasoning_output_tokens")}
        out["cost_usd"] = round((fresh * prices[0] + u.get("cached_input_tokens", 0) * prices[1]
                                 + u.get("output_tokens", 0) * prices[2]) / 1e6, 2)
        out["minutes"] = round((run.get("duration_ms") or 0) / 60000, 1)
        out["budget_stop"] = run.get("budget_stop")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("new")
    ap.add_argument("old")
    ap.add_argument("--prices", default="1,0.05,5")
    ap.add_argument("--label", default="")
    a = ap.parse_args()
    prices = [float(x) for x in a.prices.split(",")]
    sample = {}
    sp = os.path.join(HERE, "work", "sol_metrics", "sample.jsonl")
    if os.path.exists(sp):
        for line in open(sp):
            if line.strip():
                r = json.loads(line)
                sample[r["paper_id"]] = r.get("mean_human")
    ids = sorted(x.split("-", 1)[1] for x in os.listdir(a.new) if x.startswith("iclr26-"))
    rows = []
    for i in ids:
        rows.append({"paper_id": i, "mean_human": sample.get(i),
                     "new": paper(os.path.join(a.new, f"iclr26-{i}"), prices),
                     "old": paper(os.path.join(a.old, f"iclr26-{i}"), prices)})
    order = lambda key: [r["paper_id"] for r in sorted(rows, key=lambda r: -(key(r) if key(r) is not None else -1))]
    out = {"label": a.label, "n": len(rows), "prices_per_mtok": prices,
           "order_by_human": order(lambda r: r["mean_human"]),
           "order_by_new_eic_pool": order(lambda r: r["new"]["eic_pool"]),
           "order_by_old_eic_pool": order(lambda r: r["old"]["eic_pool"]),
           "order_by_new_reviewer_pool": order(lambda r: r["new"]["reviewer_pool_mean"]),
           "order_by_old_reviewer_pool": order(lambda r: r["old"]["reviewer_pool_mean"]),
           "papers": rows}
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
