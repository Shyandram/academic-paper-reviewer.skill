#!/usr/bin/env python3
"""Why GPT-6.1 Sol does not rank pilot 3's 20 papers: a diagnostic.

Reads the gitignored per-paper results under evals/work/ (Sonnet pilot 3, Sol, Terra) and the
issue-overlap annotations, and prints numbers and paper IDs only (no review or paper text), so
the output can be committed as evals/iclr2026_sol_diagnosis.json.

    python3 evals/sol_diagnosis.py > evals/iclr2026_sol_diagnosis.json

Stdlib only. The keyword categories and the "names a prior work" pattern are crude text
matches, reported as such.
"""
import json
import math
import os
import random
import re
import statistics as st
import sys

WORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work")
MODELS = [  # name, features file, results dir, issue-overlap dir
    ("sonnet", "full_metrics2/features.jsonl", "results_pilot3", "issue_overlap/iclr26_pilot3"),
    ("sol", "sol_metrics/features.jsonl", "results_sol", "issue_overlap/gpt_sol"),
    ("terra", "codex_metrics/features.jsonl", "results_terra", "issue_overlap/gpt_terra"),
]
DIMS = ["technical_rigor", "novelty", "significance", "experimental_validation", "clarity",
        "reproducibility"]
CATS = [
    ("novelty", r"novel|prior work|related work|incremental|similar to|already (been )?(explored|proposed)"
                r"|existing (work|method|approach)|known|resembl|not new|originality|subsum|differentiat"
                r"|positioning|cite"),
    ("theory", r"theorem|proof|lemma|proposition|bound|assumption|derivation|equation|convergence|formal|math"),
    ("experiments", r"baseline|ablation|experiment|benchmark|dataset|evaluat|compar|seed|variance|statistic"
                    r"|significance test|scale|empirical"),
    ("clarity", r"clar|unclear|writing|presentation|notation|figure|explain|confus|organiz|motivat"),
]
CITE = re.compile(r"et al\.?|\(\d{4}\)|\b(19|20)\d{2}\b|\[\d+\]")


def jsonl(path):
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def by_id(path):
    return {r["paper_id"]: r for r in jsonl(path)}


def rank(x):
    order = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(x):
        j = i
        while j + 1 < len(x) and x[order[j + 1]] == x[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(a, b):
    ra, rb = rank(a), rank(b)
    ma, mb = st.mean(ra), st.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else 0.0


def category(text):
    t = text.lower()
    for name, rx in CATS:
        if re.search(rx, t):
            return name
    return "other"


def issue_hits(root):
    hit = {c: 0 for c, _ in CATS + [("other", "")]}
    tot = dict(hit)
    for pid in sorted(os.listdir(root)):
        f, k = os.path.join(root, pid, "issues.json"), os.path.join(root, pid, "blind_key.json")
        if not os.path.exists(f):
            continue
        d, key = json.load(open(f)), json.load(open(k))
        human = "P" if [v for kk, v in key.items() if kk.startswith("P")][0][0] == "H" else "Q"
        if human == "P":
            ids = {x["p_issue"] for x in d["cross"] if x.get("match")}
        else:
            ids = {m for x in d["cross"] for m in x.get("match", [])}
        for iss in d["issues"][human]:
            c = category(iss["summary"])
            tot[c] += 1
            hit[c] += iss["id"] in ids
    return {c: {"hit": hit[c], "of": tot[c], "rate": round(hit[c] / tot[c], 2) if tot[c] else None}
            for c in tot}


def effort(root, pid):
    r = json.load(open(os.path.join(WORK, root, f"iclr26-{pid}", "run.json")))
    if "modelUsage" in r:
        m = list(r["modelUsage"].values())[0]
        out, reason = m["outputTokens"], m.get("thinkingTokens")
    else:
        out, reason = r["usage"]["output_tokens"], r["usage"].get("reasoning_output_tokens")
    return out, reason, r["duration_ms"] / 60000


def count_lines(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return sum(1 for line in f if line.strip())


def main():
    sample = by_id(os.path.join(WORK, "sol_metrics/sample.jsonl"))
    feats = {n: by_id(os.path.join(WORK, f)) for n, f, _, _ in MODELS}
    ids = sorted(feats["sol"])
    human = [sample[i]["mean_human"] for i in ids]
    out = {"note": "Diagnostic for GPT-6.1 Sol (high) vs Sonnet high (pilot 3) and GPT-6.1 Terra high on "
                   "pilot 3's 20 ICLR 2026 papers. Spearman vs mean human rating; numbers and paper IDs only. "
                   "Produced by evals/sol_diagnosis.py.",
           "n": len(ids)}

    out["spearman_vs_human"] = {
        n: {k: round(spearman([feats[n][i][k] for i in ids], human), 2)
            for k in ["official_rating", "reviewer_pool", "eic_pool", "rating"]}
        for n, *_ in MODELS}

    random.seed(0)
    k = "official_rating"
    diffs = []
    for _ in range(5000):
        s = [random.choice(ids) for _ in ids]
        h = [sample[i]["mean_human"] for i in s]
        diffs.append(spearman([feats["sonnet"][i][k] for i in s], h)
                     - spearman([feats["sol"][i][k] for i in s], h))
    diffs.sort()
    out["paired_bootstrap_sonnet_minus_sol_panel_rating"] = {
        "diff": round(out["spearman_vs_human"]["sonnet"][k] - out["spearman_vs_human"]["sol"][k], 2),
        "ci95": [round(diffs[125], 2), round(diffs[-126], 2)],
        "p_diff_le_0": round(sum(d <= 0 for d in diffs) / len(diffs), 3),
        "resamples": 5000}

    pool = lambda n: [feats[n][i]["reviewer_pool"] for i in ids]
    out["reviewer_pool_spearman_between_models"] = {
        "sol~sonnet": round(spearman(pool("sol"), pool("sonnet")), 2),
        "sol~terra": round(spearman(pool("sol"), pool("terra")), 2),
        "terra~sonnet": round(spearman(pool("terra"), pool("sonnet")), 2)}

    out["dimension_spearman_vs_human"] = {
        n: {d: round(spearman([feats[n][i]["dims"][d] for i in ids], human), 2) for d in DIMS}
        for n, *_ in MODELS}
    out["dimension_spearman_vs_own_reviewer_pool"] = {
        n: {d: round(spearman([feats[n][i]["dims"][d] for i in ids], pool(n)), 2) for d in DIMS}
        for n, *_ in MODELS}

    by_h = sorted(ids, key=lambda i: -sample[i]["mean_human"])
    top, bot = by_h[:10], by_h[10:]
    out["human_top10_vs_bottom10"] = {
        n: {"reviewer_pool": [round(st.mean(feats[n][i]["reviewer_pool"] for i in top), 1),
                              round(st.mean(feats[n][i]["reviewer_pool"] for i in bot), 1)],
            "panel_rating": [round(st.mean(feats[n][i]["official_rating"] for i in top), 2),
                             round(st.mean(feats[n][i]["official_rating"] for i in bot), 2)]}
        for n, *_ in MODELS}

    hr = [20 - x for x in rank(human)]
    ranks = {n: [20 - x for x in rank(pool(n))] for n, *_ in MODELS}
    out["per_paper"] = [
        {"paper_id": i, "mean_human": sample[i]["mean_human"], "human_rank": hr[j],
         **{f"{n}_pool": feats[n][i]["reviewer_pool"] for n, *_ in MODELS},
         **{f"{n}_pool_rank": ranks[n][j] for n, *_ in MODELS},
         "sonnet_rigor": feats["sonnet"][i]["dims"]["technical_rigor"],
         "sol_rigor": feats["sol"][i]["dims"]["technical_rigor"],
         "sol_iclr_rating": feats["sol"][i]["rating"], "sonnet_iclr_rating": feats["sonnet"][i]["rating"]}
        for j, i in sorted(enumerate(ids), key=lambda t: hr[t[0]])]

    out["top_concerns_naming_prior_work"] = {}
    out["effort_median"] = {}
    out["search_median"] = {}
    for n, _, root, _ in MODELS:
        papers = total = cites = 0
        for i in ids:
            tc = json.load(open(os.path.join(WORK, root, f"iclr26-{i}", "summary.json"))).get("top_concerns", [])
            tc = [t if isinstance(t, str) else json.dumps(t) for t in tc]
            c = [bool(CITE.search(t)) for t in tc]
            total += len(tc)
            cites += sum(c)
            papers += any(c)
        out["top_concerns_naming_prior_work"][n] = {"papers": papers, "of": len(ids),
                                                    "share_of_concerns": round(cites / total, 2) if total else None}
        e = [effort(root, i) for i in ids]
        out["effort_median"][n] = {
            "output_tokens": int(st.median(x[0] for x in e)),
            "reasoning_tokens": int(st.median(x[1] for x in e if x[1] is not None)),
            "minutes": round(st.median(x[2] for x in e), 1)}
        led = [count_lines(os.path.join(WORK, root, f"iclr26-{i}", "search_ledger.jsonl")) for i in ids]
        kept = [count_lines(os.path.join(WORK, root, f"iclr26-{i}", "kept_results.jsonl")) for i in ids]
        out["search_median"][n] = {
            "ledger_entries": st.median(x for x in led if x is not None),
            "kept_results": st.median(x for x in kept if x is not None)}

    out["human_issue_hit_rate_by_keyword_category"] = {
        n: issue_hits(os.path.join(WORK, ov)) for n, _, _, ov in MODELS}
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
