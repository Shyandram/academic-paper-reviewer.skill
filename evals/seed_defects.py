#!/usr/bin/env python3
"""Plant known defects in a paper's blinded text, for a seeded-defect evaluation.

A seed spec (committed) holds no manuscript text. Each seed finds its line by the SHA-256
of the stripped line (plus an occurrence index when the line repeats) and then either
changes one number in it or inserts a sentence we wrote. The spec also holds what a
review must say to count as finding the seed; that part never reaches the reviewer,
because the workflow applies the seeds in the prepare job and ships only blinded.txt.

    python3 -I evals/seed_defects.py check SPEC PAPERS_DIR     # every anchor resolves
    python3 -I evals/seed_defects.py apply SPEC PAPERS_DIR     # rewrite blinded.txt in place
    python3 -I evals/seed_defects.py anchor PAPER_TXT LINE     # authoring: sha and numbers of a line
    python3 -I evals/seed_defects.py screen SPEC RESULTS_DIR   # keyword pre-screen of reviews (local only)

PAPERS_DIR and RESULTS_DIR hold iclr26-<id>/ directories. Ops:
  replace_number  {"anchor", "number_index", "old", "new"}  the number_index-th number in
                  the line must equal "old"; it becomes "new"
  insert_after    {"anchor", "text"}  a new line after the anchor line
Anchors: {"sha256": <of the stripped line>, "occurrence": 0}. Stdlib only.
"""
import argparse
import hashlib
import json
import os
import re
import sys

NUM = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])")


def line_sha(line):
    return hashlib.sha256(line.strip().encode()).hexdigest()


def find(lines, anchor):
    hits = [i for i, l in enumerate(lines) if l.strip() and line_sha(l) == anchor["sha256"]]
    k = anchor.get("occurrence", 0)
    if k >= len(hits):
        raise ValueError(f"anchor {anchor['sha256'][:12]} occurrence {k} not found ({len(hits)} matches)")
    return hits[k]


def apply_seeds(text, seeds):
    """Return the seeded text. All anchors are resolved on the original text first, so
    the order of seeds does not matter; insertions are applied bottom-up."""
    lines = text.split("\n")
    plan = []
    for s in seeds:
        i = find(lines, s["anchor"])
        plan.append((i, s))
    if len({i for i, _ in plan}) != len(plan):
        raise ValueError("two seeds share a line")
    for i, s in sorted(plan, key=lambda p: -p[0]):
        if s["op"] == "replace_number":
            ms = list(NUM.finditer(lines[i]))
            k = s["number_index"]
            if k >= len(ms) or ms[k].group() != s["old"]:
                raise ValueError(f"{s['id']}: number {k} is not {s['old']}")
            if s["new"] == s["old"]:
                raise ValueError(f"{s['id']}: new equals old")
            m = ms[k]
            lines[i] = lines[i][:m.start()] + s["new"] + lines[i][m.end():]
        elif s["op"] == "insert_after":
            if not s.get("text", "").strip():
                raise ValueError(f"{s['id']}: empty text")
            lines.insert(i + 1, s["text"])
        else:
            raise ValueError(f"{s['id']}: unknown op {s['op']}")
    return "\n".join(lines)


def load(spec):
    with open(spec) as f:
        d = json.load(f)
    ids = [s["id"] for p in d["papers"].values() for s in p["seeds"]]
    if len(ids) != len(set(ids)):
        raise ValueError("seed ids must be unique")
    return d


def each_paper(d, root):
    for pid, p in sorted(d["papers"].items()):
        path = os.path.join(root, f"iclr26-{pid}", "blinded.txt")
        yield pid, p, path


def cmd_check(a, write=False):
    d = load(a.spec)
    n = 0
    for pid, p, path in each_paper(d, a.papers):
        if not os.path.exists(path):
            if write:
                continue  # this run did not fetch the paper
            raise ValueError(f"{pid}: no blinded.txt")
        with open(path) as f:
            text = f.read()
        out = apply_seeds(text, p["seeds"])
        n += len(p["seeds"])
        if write:
            with open(path, "w") as f:
                f.write(out)
    print(f"{'applied' if write else 'checked'} {n} seeds")
    return 0


def cmd_anchor(a):
    with open(a.paper) as f:
        lines = f.read().split("\n")
    i = a.line - 1
    sha = line_sha(lines[i])
    occ = sum(1 for l in lines[:i] if l.strip() and line_sha(l) == sha)
    print(json.dumps({"sha256": sha, "occurrence": occ,
                      "numbers": [m.group() for m in NUM.finditer(lines[i])]}))
    return 0


def cmd_screen(a):
    """For each seed, the review lines that contain any of its keywords (case-insensitive).
    A pre-screen for adjudication; the decision follows the rubric in the preregistration."""
    d = load(a.spec)
    out = {}
    for pid, p, _ in each_paper(d, a.results):
        rv = os.path.join(a.results, f"iclr26-{pid}", "review.md")
        if not os.path.exists(rv):
            continue
        with open(rv, errors="replace") as f:
            lines = f.read().split("\n")
        for s in p["seeds"]:
            kws = [k.lower() for k in s.get("keywords", [])]
            hits = [i + 1 for i, l in enumerate(lines) if any(k in l.lower() for k in kws)]
            out[s["id"]] = {"paper": pid, "type": s["type"], "candidate_lines": hits}
    json.dump(out, sys.stdout, indent=1)
    print()
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("check", "apply"):
        s = sub.add_parser(name)
        s.add_argument("spec")
        s.add_argument("papers")
    s = sub.add_parser("anchor")
    s.add_argument("paper")
    s.add_argument("line", type=int)
    s = sub.add_parser("screen")
    s.add_argument("spec")
    s.add_argument("results")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "check":
            return cmd_check(a)
        if a.cmd == "apply":
            return cmd_check(a, write=True)
        if a.cmd == "anchor":
            return cmd_anchor(a)
        return cmd_screen(a)
    except (ValueError, KeyError) as e:
        print(f"seed_defects: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
