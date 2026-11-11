#!/usr/bin/env python3
"""How much of the paper a Codex review actually saw.

The Codex CLI truncates each tool output it passes to GPT-6.x models to about 10,000
tokens, cutting the middle (`truncation_policy` {"mode": "tokens", "limit": 10000} in
codex-rs/models-manager/models.json, rust-v0.167.0). The event log keeps the full output,
so a review that `cat`s a 60 KB paper looks complete there while the model saw only the
head and tail. This script replays each run's command outputs with that truncation and
reports the share of the paper's text lines that appeared in at least one visible output.

    python3 evals/codex_read_coverage.py evals/work/results_terra [more result dirs...]

Approximation: 1 token ~ 4 bytes, so outputs over 40,000 characters keep their first and
last 20,000. A line counts as seen when it (stripped, at least 25 characters) occurs in a
visible portion. Numbers and paper IDs only. Stdlib only.
"""
import json
import os
import statistics as st
import sys

LIMIT_CHARS = 40_000
MIN_LINE = 25
HERE = os.path.dirname(os.path.abspath(__file__))


def visible(out):
    if len(out) <= LIMIT_CHARS:
        return [out]
    half = LIMIT_CHARS // 2
    return [out[:half], out[-half:]]


def coverage(run_dir, paper_txt):
    lines = [l.strip() for l in open(paper_txt, errors="replace") if len(l.strip()) >= MIN_LINE]
    if not lines:
        return None
    seen_full, seen_vis = set(), set()
    ev = os.path.join(run_dir, "codex_events.jsonl")
    if not os.path.exists(ev):
        return None
    truncated_reads = 0
    for raw in open(ev, errors="replace"):
        try:
            e = json.loads(raw)
        except ValueError:
            continue
        it = e.get("item") or {}
        if e.get("type") != "item.completed" or it.get("type") != "command_execution":
            continue
        out = it.get("aggregated_output") or ""
        if not out:
            continue
        parts = visible(out)
        hit_any = False
        for i, l in enumerate(lines):
            if l in out:
                seen_full.add(i)
                hit_any = True
                if any(l in p for p in parts):
                    seen_vis.add(i)
        truncated_reads += hit_any and len(parts) > 1
    n = len(lines)
    return {"lines": n, "seen_in_log": round(len(seen_full) / n, 3), "seen_by_model": round(len(seen_vis) / n, 3),
            "truncated_paper_reads": truncated_reads}


def main():
    out = {"note": "Share of the paper's text lines (>= 25 chars) in a model-visible tool output, replaying "
                   "Codex's 10,000-token middle truncation (approx. 40,000 chars). evals/codex_read_coverage.py.",
           "runs": {}}
    for root in sys.argv[1:]:
        rows = {}
        for d in sorted(os.listdir(root)):
            if not d.startswith("iclr26-"):
                continue
            paper = os.path.join(HERE, "work", "papers", d, "blinded.txt")
            if os.path.exists(paper):
                c = coverage(os.path.join(root, d), paper)
                if c:
                    rows[d[7:]] = c
        vis = [r["seen_by_model"] for r in rows.values()]
        out["runs"][os.path.basename(root.rstrip("/"))] = {
            "n": len(rows),
            "median_seen_by_model": round(st.median(vis), 3) if vis else None,
            "min_seen_by_model": min(vis) if vis else None,
            "papers_below_90pct": sum(v < 0.9 for v in vis),
            "per_paper": rows}
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
