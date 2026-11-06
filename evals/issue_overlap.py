#!/usr/bin/env python3
"""Issue overlap and hit rate: the skill's reviewer panel against the human reviewers.

For each paper, the weakness sections of the human reviews and of the skill's five reports
are split into atomic points and grouped into issues, within each panel and across the two
panels, by one annotator agent per paper (`evals/issue_overlap_prompt.md`). The annotator
sees the two panels under random names (P, Q), in random reviewer order, without roles.
This script prepares those inputs and computes the metrics from the annotations.

    prepare   build <out>/<id>/blind.json and blind_key.json from the human reviews
              (JerMa88/ICLR_Peer_Reviews_2026 parquet) and the skill's results
    analyze   overlap within each panel, hit rate across panels, per-role contribution
              and the coverage curve; JSON (numbers and paper ids only) and Markdown
    agree     compare two annotations of the same papers (annotator stability)
    misses    export each human main issue with its status (hit, minor_only, related,
              missed) for labeling with `evals/issue_miss_prompt.md`
    categories  hit rate per label (topic, evidence needed, reason missed); numbers only
    match-prepare / match-score   an extra list of items (the Gap Scout's) against the
              human issues, mixed with the panel's issues for one annotator
              (`evals/gap_match_prompt.md`): hit rate of panel, list and both

Annotate each prepared paper by giving an agent `evals/issue_overlap_prompt.md` with
{DIR} = <out>/<id> and {OUT} = issues.json. The inputs hold review text: keep <out> under
evals/work/ (git-ignored). Only `analyze --json` output, which holds numbers, is committed.
`prepare` needs pyarrow; everything else is standard library.
"""
import argparse
import itertools
import json
import random
import re
import statistics
import sys
from pathlib import Path

ROLES = ["R1", "R2", "R3", "R4", "DA"]
VOTING = ["R1", "R2", "R3", "R4"]
GAP = "GAP"  # the Gap Scout list (skill 2.11), included with `prepare --with-gaps`


# ---------------------------------------------------------------- prepare

def section(text, title):
    """The body of the first heading starting with `title`, up to the next heading of the
    same or a higher level. Sub-items such as "### W1", "### CRITICAL Issues" stay inside."""
    m = re.search(r"^(#{2,4}) " + title + r".*$", text, re.M)
    if not m:
        return ""
    rest = text[m.end():]
    e = re.search(r"^#{1,%d} (?!W\d|CRITICAL|MAJOR|MINOR)" % len(m.group(1)), rest, re.M)
    return rest[:e.start() if e else len(rest)].strip()


def weaknesses(report, role):
    if role == GAP:
        return section(report, "Anticipated Reviewer Concerns") or report.strip()
    return section(report, "Issue List" if role == "DA" else "Weaknesses")


def ai_reports(res, gaps=False):
    """The AI reports of one result directory, keyed by role.

    Split and check pipelines: reports/<role>/report.md. Up to skill 2.10 the Devil's
    Advocate is a fifth reviewer (reports/DA); in 2.11 the Report Checker ran it after
    the check (check/da.md), so DA comes from there when present. Single pipeline: the
    "## Reviewer:" sections of review.md (five; in 2.11 four plus a "Devil's Advocate
    Report"). With `gaps`, also the Gap Scout list (gaps/gaps.md)."""
    res = Path(res)
    if all((res / "reports" / r / "report.md").exists() for r in VOTING):
        out = {r: (res / "reports" / r / "report.md").read_text(encoding="utf-8")
               for r in VOTING}
        for da in (res / "reports" / "DA" / "report.md", res / "check" / "da.md"):
            if da.exists():
                out["DA"] = da.read_text(encoding="utf-8")
                break
    else:
        review = res / "review.md"
        if not review.exists():
            return None
        text = review.read_text(encoding="utf-8")
        parts = re.split(r"^## Reviewer: .*$", text, flags=re.M)[1:6]
        if len(parts) == 5:
            out = dict(zip(ROLES, parts))
        elif len(parts) == 4:
            out = dict(zip(VOTING, parts))
            m = re.search(r"^#{1,3} Devil'?s Advocate (?:Report|challenge).*$", text, re.M | re.I)
            if m:
                out["DA"] = text[m.end():]
                # The DA text is not part of the preceding reviewer's section.
                for r in VOTING:
                    out[r] = out[r].split(m.group(0))[0]
        else:
            return None
    if gaps and (res / "gaps" / "gaps.md").exists():
        out[GAP] = (res / "gaps" / "gaps.md").read_text(encoding="utf-8")
    return out


def human_weaknesses(parquet, ids):
    import pyarrow.parquet as pq
    t = pq.read_table(parquet, columns=["paper_id", "reviewer_id", "api_raw_review", "review_src"],
                      filters=[("paper_id", "in", list(ids))]).to_pydict()
    out = {}
    for pid, rid, raw, src in zip(t["paper_id"], t["reviewer_id"], t["api_raw_review"],
                                  t["review_src"]):
        if src != "openreview" or not raw:
            continue
        w = json.loads(raw).get("content", {}).get("weaknesses")
        w = w.get("value") if isinstance(w, dict) else w
        if w and w.strip():
            out.setdefault(pid, {})[rid] = w.strip()
    return out


def blind(paper, human, ai, rnd):
    """Random panel names and reviewer order; the key maps them back."""
    h = list(human.items())
    a = list(ai.items())
    rnd.shuffle(h)
    rnd.shuffle(a)
    names = ["P", "Q"]
    rnd.shuffle(names)
    panels, key = {}, {}
    for name, rows, src in ((names[0], h, "H"), (names[1], a, "A")):
        panels["panel_" + name] = []
        for i, (who, text) in enumerate(rows):
            rid = f"{name}{i + 1}"
            key[rid] = [src, who]
            panels["panel_" + name].append({"reviewer": rid, "weaknesses": text})
    return {"paper": paper, **panels}, key


def cmd_prepare(a):
    results = Path(a.results)
    runs = {}
    for d in sorted(results.iterdir()):
        pid = d.name.split("-", 1)[-1]
        reps = ai_reports(d, a.with_gaps) if d.is_dir() else None
        if reps:
            runs[pid] = {r: weaknesses(t, r) for r, t in reps.items()}
    human = human_weaknesses(a.reviews, runs)
    rnd = random.Random(a.seed)
    out = Path(a.out)
    n = 0
    for pid, ai in runs.items():
        empty = [r for r, t in ai.items() if not t]
        if pid not in human or empty:
            print(f"skip {pid}: " + ("no human reviews" if pid not in human
                                     else "no weaknesses found for " + ",".join(empty)),
                  file=sys.stderr)
            continue
        data, key = blind(pid, human[pid], ai, rnd)
        d = out / pid
        d.mkdir(parents=True, exist_ok=True)
        (d / "blind.json").write_text(json.dumps(data, indent=1, ensure_ascii=False))
        (d / "blind_key.json").write_text(json.dumps(key))
        n += 1
    print(f"prepared {n} papers in {out}", file=sys.stderr)


# ---------------------------------------------------------------- analyze

def mean(x):
    x = [v for v in x if v is not None and v == v]
    return statistics.mean(x) if x else None


def boot(values, reps=2000, seed=0):
    v = [x for x in values if x is not None and x == x]
    if len(v) < 2:
        return None, None
    r = random.Random(seed)
    m = sorted(statistics.mean(v[r.randrange(len(v))] for _ in v) for _ in range(reps))
    return m[int(0.025 * reps)], m[int(0.975 * reps) - 1]


def jaccard(sets):
    js = [len(sets[x] & sets[y]) / len(sets[x] | sets[y])
          for x, y in itertools.combinations(sorted(sets), 2) if sets[x] | sets[y]]
    return mean(js)


def load_paper(d, fname, major_only=True):
    """Issues per panel ({"H": [...], "A": [...]}), each a set of reviewer labels; the
    cross-panel matches (both directions); reviewer labels per panel; AI label -> role."""
    ann = json.loads((d / fname).read_text())
    key = json.loads((d / "blind_key.json").read_text())
    src = {rid[0]: v[0] for rid, v in key.items()}
    pts = {p["id"]: p for p in ann["points"]}
    issues = {}
    for letter, lst in ann["issues"].items():
        rows = []
        for i in lst:
            members = [pts[x] for x in i["points"] if x in pts]
            if not members or (major_only and all(m.get("minor") for m in members)):
                continue
            rows.append({"id": i["id"], "revs": {m["reviewer"] for m in members}})
        issues[src[letter]] = rows
    match = {}
    for c in ann.get("cross", []):
        for q in c.get("match", []):
            match.setdefault(c["p_issue"], set()).add(q)
            match.setdefault(q, set()).add(c["p_issue"])
    revs = {s: sorted(k for k, v in key.items() if v[0] == s) for s in ("H", "A")}
    role = {k: v[1] for k, v in key.items() if v[0] == "A"}
    return issues, match, revs, role


def paper_metrics(issues, match, revs, role):
    H, A = issues["H"], issues["A"]
    a_by = {i["id"]: i for i in A}

    def hit_by(h_issue, reviewers):
        return any(a_by[q]["revs"] & reviewers for q in match.get(h_issue["id"], ()) if q in a_by)

    def matched(i):
        return bool(match.get(i["id"]))

    m = {}
    voting = [r for r in revs["A"] if role[r] in VOTING]
    five = {r for r in revs["A"] if role[r] in ROLES}
    for name, panel, labels in (("human", H, revs["H"]), ("ai", A, revs["A"])):
        m[f"{name}_issues"] = len(panel)
        m[f"{name}_solo"] = mean([len(i["revs"]) == 1 for i in panel])
        m[f"{name}_jaccard"] = jaccard({r: {i["id"] for i in panel if r in i["revs"]}
                                        for r in labels})
    sub = [dict(i, revs=i["revs"] & set(voting)) for i in A]
    sub = [i for i in sub if i["revs"]]
    m["ai4_solo"] = mean([len(i["revs"]) == 1 for i in sub])
    m["ai4_jaccard"] = jaccard({r: {i["id"] for i in sub if r in i["revs"]} for r in voting})
    m["human_reviewers"] = len(revs["H"])
    allA = set(revs["A"])
    m["hit"] = mean([hit_by(h, allA) for h in H])
    m["hit_consensus"] = mean([hit_by(h, allA) for h in H if len(h["revs"]) >= 2])
    m["hit_single"] = mean([hit_by(h, allA) for h in H if len(h["revs"]) == 1])
    m["hit_without_da"] = mean([hit_by(h, set(voting)) for h in H])
    m["hit_panel"] = mean([hit_by(h, five) for h in H])
    m["ai_also_human"] = mean([matched(i) for i in A])
    # One human reviewer's issues: raised by the other humans, or hit by k AI reviewers.
    loo, k1, k3, k5 = [], [], [], []
    for h in revs["H"]:
        mine = [i for i in H if h in i["revs"]]
        if not mine:
            continue
        loo.append(mean([len(i["revs"] - {h}) > 0 for i in mine]))
        k5.append(mean([hit_by(i, allA) for i in mine]))
        k3.append(mean([mean([hit_by(i, set(c)) for i in mine])
                        for c in itertools.combinations(revs["A"], 3)]))
        k1.append(mean([mean([hit_by(i, {c}) for i in mine]) for c in revs["A"]]))
    m["human_by_other_humans"] = mean(loo)
    m["human_by_ai1"], m["human_by_ai3"], m["human_by_ai5"] = mean(k1), mean(k3), mean(k5)
    m["coverage_curve"] = [mean([mean([hit_by(h, set(c)) for h in H])
                                 for c in itertools.combinations(revs["A"], k)])
                           for k in range(1, len(revs["A"]) + 1)]
    by_role = {role[r]: r for r in revs["A"]}
    sets = {ro: {i["id"] for i in A if lab in i["revs"]} for ro, lab in by_role.items()}
    m["roles"] = {}
    for ro, lab in by_role.items():
        others = set().union(*(s for o, s in sets.items() if o != ro))
        own = sets[ro]
        hit_own = {h["id"] for h in H if hit_by(h, {lab})}
        hit_oth = {h["id"] for h in H if hit_by(h, allA - {lab})}
        m["roles"][ro] = {
            "issues": len(own),
            "own_only": len(own - others) / len(own) if own else None,
            "jaccard_with_others": mean([len(own & s) / len(own | s)
                                         for o, s in sets.items() if o != ro and own | s]),
            "hit": len(hit_own) / len(H) if H else None,
            "unique_hit": len(hit_own - hit_oth) / len(H) if H else None,
        }
    return m


METRICS = [
    ("human_issues", "Human: main issues per paper"),
    ("ai_issues", "AI: main issues per paper"),
    ("human_solo", "Human: share of issues raised by one reviewer"),
    ("ai_solo", "AI (all sources): share of issues raised by one reviewer"),
    ("ai4_solo", "AI (R1-R4): share of issues raised by one reviewer"),
    ("human_jaccard", "Human: pairwise Jaccard between reviewers"),
    ("ai_jaccard", "AI (all sources): pairwise Jaccard between reviewers"),
    ("ai4_jaccard", "AI (R1-R4): pairwise Jaccard between reviewers"),
    ("hit", "Hit rate: human issues raised by the AI panel"),
    ("hit_consensus", "  of those raised by 2+ humans"),
    ("hit_single", "  of those raised by one human"),
    ("hit_without_da", "  by the AI panel without the DA"),
    ("hit_panel", "  by the five reviewers (without the Gap Scout)"),
    ("ai_also_human", "AI issues also raised by a human"),
    ("human_by_other_humans", "One human's issues raised by the other humans"),
    ("human_by_ai1", "One human's issues raised by 1 AI reviewer"),
    ("human_by_ai3", "One human's issues raised by 3 AI reviewers"),
    ("human_by_ai5", "One human's issues raised by the AI panel (5)"),
]


def analyze(base, fname="issues.json", ids=None, major_only=True, reps=2000):
    rows = []
    for d in sorted(Path(base).iterdir()):
        if not (d / fname).exists() or (ids and d.name not in ids):
            continue
        m = paper_metrics(*load_paper(d, fname, major_only))
        m["paper_id"] = d.name
        rows.append(m)
    summary = {"n": len(rows), "major_only": major_only, "annotation": fname, "metrics": {}}
    for k, label in METRICS:
        v = [r[k] for r in rows]
        lo, hi = boot(v, reps)
        summary["metrics"][k] = {"label": label, "mean": r3(mean(v)), "ci95": [r3(lo), r3(hi)]}
    n_ai = max((len(r["coverage_curve"]) for r in rows), default=0)
    summary["coverage_curve"] = [r3(mean([r["coverage_curve"][k] for r in rows
                                          if len(r["coverage_curve"]) > k]))
                                 for k in range(n_ai)]
    summary["roles"] = {ro: {f: r3(mean([r["roles"][ro][f] for r in rows if ro in r["roles"]]))
                             for f in ("issues", "own_only", "jaccard_with_others", "hit",
                                       "unique_hit")}
                        for ro in ROLES + [GAP] if any(ro in r["roles"] for r in rows)}
    return summary, rows


def r3(x):
    return None if x is None else round(x, 3)


def markdown(s):
    out = [f"Papers: {s['n']} ({'main issues only' if s['major_only'] else 'all issues'})", "",
           "| Metric | Mean | 95% CI |", "|---|---|---|"]
    for k, v in s["metrics"].items():
        ci = "–" if v["ci95"][0] is None else f"{v['ci95'][0]:.2f}–{v['ci95'][1]:.2f}"
        out.append(f"| {v['label']} | {v['mean']:.2f} | {ci} |" if v["mean"] is not None
                   else f"| {v['label']} | – | – |")
    out += ["", "Coverage of the human issues by k AI reviewers (mean over subsets): "
            + ", ".join(f"k={i + 1} {c:.2f}" for i, c in enumerate(s["coverage_curve"])), "",
            "| Role | Issues | Raised by no one else | Jaccard with others | Human issues hit | Hit by no other role |",
            "|---|---|---|---|---|---|"]
    for ro, v in s["roles"].items():
        cells = ["–" if v[f] is None else (f"{v[f]:.1f}" if f == "issues" else f"{v[f]:.2f}")
                 for f in ("issues", "own_only", "jaccard_with_others", "hit", "unique_hit")]
        out.append(f"| {ro} | " + " | ".join(cells) + " |")
    return "\n".join(out)


def cmd_analyze(a):
    ids = set(a.ids.split(",")) if a.ids else None
    s, rows = analyze(a.dir, a.annotation, ids, not a.all_issues, a.reps)
    if a.json:
        keep = {k: v for k, v in s.items()}
        keep["papers"] = [{k: (r3(v) if isinstance(v, float) else v) for k, v in r.items()
                           if k != "roles"} for r in rows]
        Path(a.json).write_text(json.dumps(keep, indent=1))
    print(markdown(s))


def cmd_agree(a):
    ids = sorted(d.name for d in Path(a.dir).iterdir()
                 if (d / a.first).exists() and (d / a.second).exists())
    s1, _ = analyze(a.dir, a.first, set(ids), reps=500)
    s2, _ = analyze(a.dir, a.second, set(ids), reps=500)
    print(f"Papers annotated twice: {len(ids)}\n\n| Metric | {a.first} | {a.second} | Difference |\n|---|---|---|---|")
    for k, v in s1["metrics"].items():
        x, y = v["mean"], s2["metrics"][k]["mean"]
        d = "–" if x is None or y is None else f"{y - x:+.2f}"
        print(f"| {v['label']} | {x} | {y} | {d} |")



# ---------------------------------------------------------------- what the panel misses

STATUS = ("hit", "minor_only", "related", "missed")


def human_issue_status(d, fname="issues.json"):
    """Each human main issue with its status: hit (matched by an AI main issue),
    minor_only (matched only by AI minor points), related (only a partial AI overlap),
    missed. Rows hold review text: write them under evals/work/ only."""
    ann = json.loads((d / fname).read_text())
    key = json.loads((d / "blind_key.json").read_text())
    src = {rid[0]: v[0] for rid, v in key.items()}
    pts = {p["id"]: p for p in ann["points"]}
    match, related = {}, {}
    for c in ann.get("cross", []):
        for field, store in (("match", match), ("related", related)):
            for q in c.get(field, []) or []:
                store.setdefault(c["p_issue"], set()).add(q)
                store.setdefault(q, set()).add(c["p_issue"])
    ai_major, ai_text = set(), []
    for letter, lst in ann["issues"].items():
        if src[letter] != "A":
            continue
        for i in lst:
            members = [pts[x] for x in i["points"] if x in pts]
            if members and not all(m.get("minor") for m in members):
                ai_major.add(i["id"])
            ai_text.append({"id": i["id"], "summary": i.get("summary", ""),
                            "minor": i["id"] not in ai_major})
    rows = []
    for letter, lst in ann["issues"].items():
        if src[letter] != "H":
            continue
        for i in lst:
            members = [pts[x] for x in i["points"] if x in pts]
            if not members or all(m.get("minor") for m in members):
                continue
            m = match.get(i["id"], set())
            status = ("hit" if m & ai_major else "minor_only" if m
                      else "related" if related.get(i["id"]) else "missed")
            rows.append({"paper_id": d.name, "issue_id": i["id"], "status": status,
                         "n_humans": len({x["reviewer"] for x in members}),
                         "summary": i.get("summary", ""),
                         "points": [x["text"] for x in members]})
    return rows, ai_text


def cmd_misses(a):
    base, out = Path(a.dir), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for d in sorted(x for x in base.iterdir() if (x / a.annotation).exists()):
        r, ai = human_issue_status(d, a.annotation)
        rows += r
        (out / f"{d.name}_ai_issues.json").write_text(json.dumps(ai, indent=1))
    with open(out / "human_issues.jsonl", "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    n = {s: sum(r["status"] == s for r in rows) for s in STATUS}
    print(f"{len(rows)} human main issues: " + ", ".join(f"{k} {v}" for k, v in n.items()))


def by_label(rows, labels, field, reps=2000):
    """Share of human issues hit, per label value, with a bootstrap CI over papers."""
    lab = {(x["paper_id"], x["issue_id"]): x for x in labels}
    out = {}
    values = sorted({lab[k][field] for k in lab if field in lab[k]})
    for v in values:
        sel = [r for r in rows if lab.get((r["paper_id"], r["issue_id"]), {}).get(field) == v]
        papers = sorted({r["paper_id"] for r in sel})
        per = {p: [r["status"] == "hit" for r in sel if r["paper_id"] == p] for p in papers}
        rnd = random.Random(0)
        bs = []
        for _ in range(reps):
            draw = [x for p in rnd.choices(papers, k=len(papers)) for x in per[p]]
            bs.append(mean(draw))
        bs.sort()
        out[v] = {"n": len(sel), "share": len(sel) / max(len(rows), 1),
                  "hit": mean([r["status"] == "hit" for r in sel]),
                  "ci": [bs[int(0.025 * reps)], bs[int(0.975 * reps) - 1]],
                  "status": {s: sum(r["status"] == s for r in sel) for s in STATUS}}
    return out


def cmd_categories(a):
    rows = [json.loads(x) for x in open(a.issues)]
    labels = [json.loads(x) for x in open(a.labels)]
    s = {"n": len(rows), "status": {k: sum(r["status"] == k for r in rows) for k in STATUS},
         "consensus": by_label(rows, [dict(paper_id=r["paper_id"], issue_id=r["issue_id"],
                                           humans="2+" if r["n_humans"] > 1 else "1")
                                      for r in rows], "humans", a.reps)}
    for field in a.fields.split(","):
        s[field] = by_label(rows, labels, field, a.reps)
    lines = []
    for field, tab in s.items():
        if not isinstance(tab, dict) or field == "status":
            continue
        lines.append(f"\n{field}: value, n, share, hit [CI], missed+related")
        for v, x in sorted(tab.items(), key=lambda kv: -kv[1]["n"]):
            lines.append(f"  {v:28s} {x['n']:4d} {x['share']:.2f} {x['hit']:.2f} "
                         f"[{x['ci'][0]:.2f}, {x['ci'][1]:.2f}] "
                         f"{x['status']['missed'] + x['status']['related']}")
    print(f"{s['n']} human main issues; status {s['status']}" + "\n".join(lines))
    if a.json:
        Path(a.json).write_text(json.dumps(s, indent=1))


# ---------------------------------------------------------------- extra source vs the panel

def cmd_match_prepare(a):
    """For each paper: the human main issues, and the panel's main issues mixed at random
    with the items of an extra list (e.g. the Gap Scout's), without sources, for one
    annotator (`evals/gap_match_prompt.md`). Both are then judged on the same scale."""
    base, extra = Path(a.dir), Path(a.extra)
    rows = {}
    for r in map(json.loads, open(a.issues)):
        rows.setdefault(r["paper_id"], []).append(r)
    out = Path(a.out)
    for pid, hum in rows.items():
        d = base / pid
        f = extra / pid / a.extra_file
        if not f.exists():
            print(f"skip {pid}: no {f}", file=sys.stderr)
            continue
        ann = json.loads((d / a.annotation).read_text())
        key = json.loads((d / "blind_key.json").read_text())
        src = {k[0]: v[0] for k, v in key.items()}
        pts = {x["id"]: x for x in ann["points"]}
        items = []
        for letter, lst in ann["issues"].items():
            if src[letter] != "A":
                continue
            for i in lst:
                m = [pts[x] for x in i["points"] if x in pts]
                if m and not all(x.get("minor") for x in m):
                    items.append(("panel", i["id"], " / ".join(x["text"] for x in m)[:600]))
        lines = [ln[2:].strip() for ln in f.read_text(encoding="utf-8").splitlines()
                 if ln.startswith("- ")]
        items += [("extra", f"g{n}", s) for n, s in enumerate(lines)]
        random.Random(f"{a.seed}-{pid}").shuffle(items)
        o = out / pid
        o.mkdir(parents=True, exist_ok=True)
        (o / "match.json").write_text(json.dumps({
            "human": [{"id": f"H{n + 1}", "summary": r["summary"], "points": r["points"]}
                      for n, r in enumerate(hum)],
            "items": [{"id": f"X{n + 1}", "text": s} for n, (_, _, s) in enumerate(items)]},
            indent=1, ensure_ascii=False))
        (o / "match_key.json").write_text(json.dumps({
            "items": {f"X{n + 1}": [s, i] for n, (s, i, _) in enumerate(items)},
            "human": {f"H{n + 1}": r["issue_id"] for n, r in enumerate(hum)}}))
    print(f"prepared {len(list(out.glob('*/match.json')))} papers in {out}", file=sys.stderr)


def cmd_match_score(a):
    """Hit rate of the human issues by the panel, the extra list and both, as judged by
    the same annotator; and by the first k items of the extra list. Numbers only."""
    out = Path(a.dir)
    status = {(r["paper_id"], r["issue_id"]): r["status"] for r in map(json.loads, open(a.issues))}
    per, counts, n_items = {}, {}, {"panel": 0, "extra": 0}
    ks = [int(k) for k in a.k.split(",")]
    for d in sorted(x for x in out.iterdir() if (x / a.annotation).exists()):
        key = json.loads((d / "match_key.json").read_text())
        # [source, id]; any source other than "panel" is the extra list
        src = {k: ("panel" if v[0] == "panel" else "extra", v[1]) for k, v in key["items"].items()}
        for v in src.values():
            n_items[v[0]] += 1
        rows = []
        for e in json.loads((d / a.annotation).read_text()):
            hit = [src[x] for x in e.get("match", []) if x in src]
            ex = [int(v[1][1:]) for v in hit if v[0] == "extra"]
            r = {"panel": any(v[0] == "panel" for v in hit), "extra": bool(ex)}
            r["both"] = r["panel"] or r["extra"]
            r["orig_hit"] = status.get((d.name, key["human"][e["human"]])) == "hit"
            for k in ks:
                r[f"extra_top{k}"] = any(i < k for i in ex)
            rows.append(r)
        per[d.name] = rows
    papers = sorted(per)
    s = {"n_papers": len(papers), "n_human_issues": sum(len(v) for v in per.values()),
         "items_per_paper": {k: r3(v / max(len(papers), 1)) for k, v in n_items.items()},
         "hit": {}}
    for f in ["orig_hit", "panel", "extra", "both"] + [f"extra_top{k}" for k in ks]:
        pm = [mean([r[f] for r in per[p]]) for p in papers]
        lo, hi = boot(pm, a.reps)
        s["hit"][f] = {"count": sum(r[f] for p in papers for r in per[p]),
                       "mean": r3(mean(pm)), "ci95": [r3(lo), r3(hi)]}
    s["agreement_orig_vs_rejudged_panel"] = r3(mean(
        [r["orig_hit"] == r["panel"] for p in papers for r in per[p]]))
    for f, v in s["hit"].items():
        ci = "" if None in v["ci95"] else f" [{v['ci95'][0]:.2f}, {v['ci95'][1]:.2f}]"
        print(f"{f:16s} {v['count']:4d}  {v['mean']:.2f}{ci}")
    print("agreement with the original annotation:", s["agreement_orig_vs_rejudged_panel"],
          "| items per paper:", s["items_per_paper"])
    if a.json:
        Path(a.json).write_text(json.dumps(s, indent=1))


# ------------------------------------------------- per-source items from a run

def run_items(res):
    """The weakness items of one result directory, by source, for a matching pass:
    each reviewer's main weaknesses (`W<n>` headings, Minor left out), the Devil's
    Advocate issues (DA-C/DA-M rows), and the Gap Scout list with the Report Checker's
    verdict (dropped or kept) from the `Anticipated Reviewer Concerns` section of
    check/gaps_checked.md (2.10.1) or check/report_check.md (2.11). Returns
    [(source, item id, text, extra)]."""
    res = Path(res)
    reps = ai_reports(res, gaps=True) or {}
    out = []
    for r in VOTING:
        w = weaknesses(reps.get(r, ""), r)
        for m in re.finditer(r"^#{2,4} (W\d+)\b(.*?)(?=^#{2,4} |\Z)", w, re.M | re.S):
            body = " ".join(m.group(2).split())
            out.append((r, f"{r}-{m.group(1)}", body[:600], {}))
    da = weaknesses(reps.get("DA", ""), "DA")
    for m in re.finditer(r"^\| (DA-[CM]\d+) \|(.*)$", da, re.M):
        cells = [c.strip() for c in m.group(2).split("|") if c.strip()]
        out.append(("DA", m.group(1), " | ".join(cells)[:600], {}))
    dropped = set()
    # 2.10.1: check/gaps_checked.md; 2.11: a section of check/report_check.md.
    rc = next((f for f in (res / "check" / "gaps_checked.md", res / "check" / "report_check.md")
               if f.exists()), None)
    if rc:
        text = rc.read_text(encoding="utf-8")
        m = re.search(r"^(#+)[^\n]*Anticipated Reviewer Concerns[^\n]*$", text, re.M | re.I)
        if m:
            rest = text[m.end():]
            e = re.search(r"^#{1,%d} " % len(m.group(1)), rest, re.M)
            for ln in rest[:e.start() if e else len(rest)].splitlines():
                g = re.search(r"\bG(\d+)\b", ln)
                if g and re.search(r"\bdrop", ln, re.I):
                    dropped.add(int(g.group(1)))
    g = reps.get(GAP, "")
    for m in re.finditer(r"^- G(\d+)\b\s*(.*)$", g, re.M):
        n = int(m.group(1))
        # Drop the "[category]" tag, so the annotator cannot tell the Scout's items apart.
        text = re.sub(r"^\[[^\]]*\]\s*", "", m.group(2))
        out.append((GAP, f"G{n}", text[:600], {"dropped": n in dropped, "rank": n}))
    return out


def cmd_run_prepare(a):
    """Blind matching files for one run directory (skill 2.11 and 2.10.1 layouts): the human main
    issues from `misses` against every item of the run, all sources mixed at random."""
    rows = {}
    for r in map(json.loads, open(a.issues)):
        rows.setdefault(r["paper_id"], []).append(r)
    out = Path(a.out)
    for d in sorted(Path(a.results).iterdir()):
        pid = d.name.split("-", 1)[-1]
        if not d.is_dir() or pid not in rows:
            continue
        items = run_items(d)
        if not items:
            print(f"skip {pid}: no items", file=sys.stderr)
            continue
        random.Random(f"{a.seed}-{pid}").shuffle(items)
        o = out / pid
        o.mkdir(parents=True, exist_ok=True)
        hum = rows[pid]
        (o / "match.json").write_text(json.dumps({
            "human": [{"id": f"H{n + 1}", "summary": r["summary"], "points": r["points"]}
                      for n, r in enumerate(hum)],
            "items": [{"id": f"X{n + 1}", "text": s} for n, (_, _, s, _) in enumerate(items)]},
            indent=1, ensure_ascii=False))
        (o / "match_key.json").write_text(json.dumps({
            "items": {f"X{n + 1}": [src, i, ex] for n, (src, i, _, ex) in enumerate(items)},
            "human": {f"H{n + 1}": r["issue_id"] for n, r in enumerate(hum)}}))
    print(f"prepared {len(list(out.glob('*/match.json')))} papers in {out}", file=sys.stderr)


RUN_SETS = {
    "panel (R1-R4)": lambda s, x: s in VOTING,
    "Devil's Advocate": lambda s, x: s == "DA",
    "Gap Scout, all items": lambda s, x: s == GAP,
    "Gap Scout, kept by the checker": lambda s, x: s == GAP and not x.get("dropped"),
    "Gap Scout, first 20": lambda s, x: s == GAP and x.get("rank", 99) <= 20,
    "panel + DA": lambda s, x: s in VOTING or s == "DA",
    "panel + Gap Scout": lambda s, x: s in VOTING or s == GAP,
    "everything": lambda s, x: True,
}


def cmd_run_score(a):
    """Hit rate of the human main issues per source and per set of sources, unique hits
    per source, and items per paper. Numbers only."""
    out = Path(a.dir)
    status = {(r["paper_id"], r["issue_id"]): r["status"] for r in map(json.loads, open(a.issues))}
    per, n_items = {}, {}
    for d in sorted(x for x in out.iterdir() if (x / a.annotation).exists()):
        key = json.loads((d / "match_key.json").read_text())
        src = {k: (v[0], v[2] if len(v) > 2 else {}) for k, v in key["items"].items()}
        for s, x in src.values():
            n_items[s] = n_items.get(s, 0) + 1
            if s == GAP and x.get("dropped"):
                n_items["GAP dropped"] = n_items.get("GAP dropped", 0) + 1
        rows = []
        for e in json.loads((d / a.annotation).read_text()):
            hit = [src[x] for x in e.get("match", []) if x in src]
            r = {name: any(f(s, x) for s, x in hit) for name, f in RUN_SETS.items()}
            for ro in VOTING + ["DA", GAP]:
                r[f"only {ro}"] = bool(hit) and all(s == ro for s, _ in hit)
            r["pilot-3 panel hit"] = status.get((d.name, key["human"][e["human"]])) == "hit"
            rows.append(r)
        per[d.name] = rows
    papers = sorted(per)
    s = {"n_papers": len(papers), "n_human_issues": sum(len(v) for v in per.values()),
         "items_per_paper": {k: r3(v / max(len(papers), 1)) for k, v in sorted(n_items.items())},
         "hit": {}}
    fields = list(RUN_SETS) + [f"only {ro}" for ro in VOTING + ["DA", GAP]] + ["pilot-3 panel hit"]
    for f in fields:
        pm = [mean([r[f] for r in per[p]]) for p in papers]
        lo, hi = boot(pm, a.reps)
        s["hit"][f] = {"count": sum(r[f] for p in papers for r in per[p]),
                       "mean": r3(mean(pm)), "ci95": [r3(lo), r3(hi)]}
    for f, v in s["hit"].items():
        ci = "" if None in v["ci95"] else f" [{v['ci95'][0]:.2f}, {v['ci95'][1]:.2f}]"
        print(f"{f:32s} {v['count']:4d}  {v['mean']:.2f}{ci}")
    print("items per paper:", s["items_per_paper"])
    if a.json:
        Path(a.json).write_text(json.dumps(s, indent=1))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("prepare")
    s.add_argument("--reviews", required=True, help="JerMa88 ICLR 2026 reviews parquet")
    s.add_argument("--results", required=True, help="directory of <prefix>-<id> result dirs")
    s.add_argument("--out", required=True, help="output dir (keep it under evals/work/)")
    s.add_argument("--seed", type=int, default=7)
    s.add_argument("--with-gaps", action="store_true",
                   help="also include the Gap Scout list (gaps/gaps.md) as an AI source")
    s.set_defaults(fn=cmd_prepare)
    s = sub.add_parser("analyze")
    s.add_argument("dir")
    s.add_argument("--annotation", default="issues.json")
    s.add_argument("--ids", default="", help="comma-separated paper ids to include")
    s.add_argument("--all-issues", action="store_true", help="include minor issues")
    s.add_argument("--json", help="write the numbers (no review text) to this file")
    s.add_argument("--reps", type=int, default=2000)
    s.set_defaults(fn=cmd_analyze)
    s = sub.add_parser("agree")
    s.add_argument("dir")
    s.add_argument("--first", default="issues.json")
    s.add_argument("--second", default="issues_b.json")
    s.set_defaults(fn=cmd_agree)
    s = sub.add_parser("misses", help="export the human issues with their status")
    s.add_argument("dir")
    s.add_argument("--annotation", default="issues.json")
    s.add_argument("--out", required=True, help="output dir (keep it under evals/work/)")
    s.set_defaults(fn=cmd_misses)
    s = sub.add_parser("categories", help="hit rate per category of human issue")
    s.add_argument("--issues", required=True, help="human_issues.jsonl from `misses`")
    s.add_argument("--labels", required=True, help="JSONL: paper_id, issue_id, <fields>")
    s.add_argument("--fields", default="topic,evidence,reason")
    s.add_argument("--json", help="write the numbers (no review text) to this file")
    s.add_argument("--reps", type=int, default=2000)
    s.set_defaults(fn=cmd_categories)
    s = sub.add_parser("match-prepare", help="panel + extra list vs the human issues")
    s.add_argument("dir", help="the annotated papers (with issues.json, blind_key.json)")
    s.add_argument("--issues", required=True, help="human_issues.jsonl from `misses`")
    s.add_argument("--extra", required=True, help="dir of <id>/<extra-file>, e.g. Gap Scout lists")
    s.add_argument("--extra-file", default="gaps.md")
    s.add_argument("--annotation", default="issues.json")
    s.add_argument("--out", required=True, help="output dir (keep it under evals/work/)")
    s.add_argument("--seed", type=int, default=7)
    s.set_defaults(fn=cmd_match_prepare)
    s = sub.add_parser("match-score", help="hit rate of the panel, the extra list and both")
    s.add_argument("dir", help="the match-prepare output, annotated with gap_match_prompt.md")
    s.add_argument("--issues", required=True)
    s.add_argument("--annotation", default="matched.json")
    s.add_argument("--k", default="10,20", help="also score the first k extra items")
    s.add_argument("--json", help="write the numbers (no review text) to this file")
    s.add_argument("--reps", type=int, default=2000)
    s.set_defaults(fn=cmd_match_score)
    s = sub.add_parser("run-prepare", help="per-source items of a 2.11 run vs the human issues")
    s.add_argument("--results", required=True, help="directory of <prefix>-<id> result dirs")
    s.add_argument("--issues", required=True, help="human_issues.jsonl from `misses`")
    s.add_argument("--out", required=True, help="output dir (keep it under evals/work/)")
    s.add_argument("--seed", type=int, default=7)
    s.set_defaults(fn=cmd_run_prepare)
    s = sub.add_parser("run-score", help="hit rate per source of a 2.11 run")
    s.add_argument("dir", help="the run-prepare output, annotated with gap_match_prompt.md")
    s.add_argument("--issues", required=True)
    s.add_argument("--annotation", default="matched.json")
    s.add_argument("--json", help="write the numbers (no review text) to this file")
    s.add_argument("--reps", type=int, default=2000)
    s.set_defaults(fn=cmd_run_score)
    a = ap.parse_args(argv)
    a.fn(a)


if __name__ == "__main__":
    main()
