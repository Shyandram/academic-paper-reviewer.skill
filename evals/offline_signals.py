#!/usr/bin/env python3
"""Offline checks on the 86-paper 2.10.1 evaluation (Sonnet), with no model calls.

    python3 -I evals/offline_signals.py ranking      # which of the panel's own numbers ranks best
    python3 -I evals/offline_signals.py calibration  # does a linear stretch of the panel rating help
    python3 -I evals/offline_signals.py precision    # which AI issues match a human main issue

Reads evals/work/ (gitignored): full_metrics/{sample.jsonl,splits.json},
results_full/ and results_pilot3/ (scores.json, summary.json), and issue_overlap/all86/
(issues.json, blind_key.json). Candidates are chosen on the train split and checked on the
test split; paired bootstrap CIs are over papers. Stdlib only.
"""
import argparse
import collections
import json
import os
import random
import statistics as st

W = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work")
DIMS = ["technical_rigor", "clarity", "novelty", "significance", "experimental_validation",
        "reproducibility", "ethics"]
BASE = "panel_rating"


def ranks(v):
    o = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(x, y):
    a, b = ranks(x), ranks(y)
    ma, mb = st.mean(a), st.mean(b)
    num = sum((p - ma) * (q - mb) for p, q in zip(a, b))
    den = (sum((p - ma) ** 2 for p in a) * sum((q - mb) ** 2 for q in b)) ** .5
    return num / den if den else 0.0


def auc(s, lab):
    pos = [x for x, l in zip(s, lab) if l]
    neg = [x for x, l in zip(s, lab) if not l]
    return sum((p > n) + .5 * (p == n) for p in pos for n in neg) / (len(pos) * len(neg))


def to_iclr(x):
    m = {1: 0, 2: 2, 3: 4, 4: 6, 5: 8, 6: 10}
    x = min(6.0, max(1.0, x))
    lo = min(int(x), 5)
    return m[lo] + (m[lo + 1] - m[lo]) * (x - lo)


def load():
    sample = {}
    with open(f"{W}/full_metrics/sample.jsonl") as f:
        for line in f:
            r = json.loads(line)
            sample[r["paper_id"]] = r
    with open(f"{W}/full_metrics/splits.json") as f:
        splits = json.load(f)
    feats = {}
    for d in ("results_full", "results_pilot3"):
        for n in os.listdir(f"{W}/{d}"):
            pid = n.split("-", 1)[1]
            if pid not in splits:
                continue
            with open(f"{W}/{d}/{n}/scores.json") as f:
                R = json.load(f)["reviewers"]
            with open(f"{W}/{d}/{n}/summary.json") as f:
                sm = json.load(f)
            pool = [r["pool_position"] for r in R]
            x = {BASE: st.mean(r["overall"] for r in R), "mean_pool": st.mean(pool),
                 "median_pool": st.median(pool), "min_pool": min(pool), "max_pool": max(pool),
                 "eic_pool": sm.get("eic_pool_position"),
                 "dim_mean": st.mean(st.mean(r["scores"][k] for k in DIMS) for r in R)}
            for k in DIMS:
                x["dim_" + k] = st.mean(r["scores"][k] for r in R)
            for r in R:
                x["pool_" + r["role"].split()[0]] = r["pool_position"]
            feats[pid] = x
    assert len(feats) == 86, len(feats)
    return sample, splits, feats


def paired_ci(ids, f, a, y, reps=2000):
    rnd = random.Random(0)
    out = []
    for _ in range(reps):
        s = [rnd.choice(ids) for _ in ids]
        yy = [y[p] for p in s]
        out.append(spearman([f[p][a] for p in s], yy) - spearman([f[p][BASE] for p in s], yy))
    out.sort()
    return round(out[int(.025 * reps)], 3), round(out[int(.975 * reps)], 3)


def cmd_ranking(_):
    sample, splits, f = load()
    y = {p: sample[p]["mean_human"] for p in f}
    acc = {p: sample[p]["accepted"] for p in f}
    sets = {"train": [p for p in f if splits[p] == "train"],
            "test": [p for p in f if splits[p] == "test"], "all": sorted(f)}
    names = [n for n in f[sets["all"][0]] if all(f[p][n] is not None for p in f)]
    tr = sets["train"]
    best = max((n for n in names if n != BASE),
               key=lambda n: spearman([f[p][n] for p in tr], [y[p] for p in tr]))
    out = {"selected_on_train": best, "signals": {}}
    for n in names:
        out["signals"][n] = {k: {"spearman": round(spearman([f[p][n] for p in s], [y[p] for p in s]), 3),
                                 "auc": round(auc([f[p][n] for p in s], [acc[p] for p in s]), 3)}
                             for k, s in sets.items()}
    out["selected_minus_panel_ci95"] = {k: paired_ci(sets[k], f, best, y) for k in ("test", "all")}
    print(json.dumps(out, indent=1))


def cmd_calibration(_):
    sample, splits, f = load()
    y = {p: sample[p]["mean_human"] for p in f}
    pr = {p: to_iclr(f[p][BASE]) for p in f}
    tr = [p for p in f if splits[p] == "train"]
    te = [p for p in f if splits[p] == "test"]
    xs, ys = [pr[p] for p in tr], [y[p] for p in tr]
    mx, my = st.mean(xs), st.mean(ys)
    b = sum((a - mx) * (c - my) for a, c in zip(xs, ys)) / sum((a - mx) ** 2 for a in xs)
    a = my - b * mx
    const = st.median(ys)
    nmae = lambda g: round(st.mean(abs(g(p) - y[p]) for p in te) / 10, 3)  # noqa: E731
    print(json.dumps({"fit_on_train": {"intercept": round(a, 2), "slope": round(b, 2)},
                      "test_nmae": {"panel": nmae(lambda p: pr[p]),
                                    "calibrated": nmae(lambda p: a + b * pr[p]),
                                    "constant_train_median": nmae(lambda p: const)},
                      "sd_all": {"human": round(st.pstdev(y.values()), 2),
                                 "panel": round(st.pstdev(pr.values()), 2)}}, indent=1))


def cmd_precision(_):
    """Share of AI issues (one entry per merged issue) that match a human main issue."""
    base = f"{W}/issue_overlap/all86"
    acc = collections.defaultdict(lambda: [0, 0, 0])

    def add(k, hit, rel):
        acc[k][0] += hit
        acc[k][1] += rel
        acc[k][2] += 1

    for pid in sorted(os.listdir(base)):
        p = os.path.join(base, pid)
        if not os.path.isdir(p):
            continue
        with open(f"{p}/issues.json") as fh:
            d = json.load(fh)
        with open(f"{p}/blind_key.json") as fh:
            key = json.load(fh)
        pts = {x["id"]: x for x in d["points"]}
        p_is_ai = next(v[0] for k, v in key.items() if k.startswith("P")) == "A"
        side = "P" if p_is_ai else "Q"
        hit, rel = set(), set()
        for c in d["cross"]:
            if p_is_ai:
                if c["match"]:
                    hit.add(c["p_issue"])
                if c["related"]:
                    rel.add(c["p_issue"])
            else:
                hit |= set(c["match"])
                rel |= set(c["related"])
        for i in d["issues"][side]:
            own = [pts[x] for x in i["points"] if x in pts]
            revs = {x["reviewer"] for x in own}
            roles = {key[r][1] for r in revs}
            h, r = i["id"] in hit, i["id"] in hit or i["id"] in rel
            add("all", h, r)
            add(f"raised_by_{min(len(revs), 4)}{'+' if len(revs) >= 4 else ''}_ai", h, r)
            add("minor_only" if all(x["minor"] for x in own) else "a_main_point", h, r)
            if len(roles) == 1:
                add(f"only_{next(iter(roles))}", h, r)
    print(json.dumps({k: {"n": v[2], "match": round(v[0] / v[2], 3),
                          "match_or_related": round(v[1] / v[2], 3)}
                      for k, v in sorted(acc.items())}, indent=1))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for n in ("ranking", "calibration", "precision"):
        sub.add_parser(n)
    a = ap.parse_args()
    {"ranking": cmd_ranking, "calibration": cmd_calibration, "precision": cmd_precision}[a.cmd](a)


if __name__ == "__main__":
    main()
