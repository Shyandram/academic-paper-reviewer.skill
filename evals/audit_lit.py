#!/usr/bin/env python3
"""Audit the literature-check (v2.5) evaluation runs.

    python3 evals/audit_lit.py evals/manifest_lit.json

Per run (evals/work/results/<id>-lit/):
  * leak check: any KEPT ledger entry that is the reviewed paper, judged from
    the manifest's true title and arXiv ID, not from the agent's fingerprint
  * search activity: queries, refusals, kept and dropped results
  * self-matches caught: dropped entries that were the reviewed paper
  * recommended references: how many were verified with a link
  * decision vs. the same paper reviewed without the literature check
Writes evals/REPORT_lit.md and prints it.
"""

import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"


def norm(t):
    return re.sub(r"\s+", " ", re.sub(r"[^0-9a-z]+", " ", str(t or "").lower())).strip()


def load(p):
    try:
        return json.loads(Path(p).read_text())
    except Exception:
        return None


def is_self(entry, title, arxiv_id):
    if difflib.SequenceMatcher(None, norm(entry.get("title")), norm(title)).ratio() >= 0.8:
        return True
    return arxiv_id in str(entry.get("url") or "")


def baseline_final(base_id):
    base_id = base_id.replace("-plag", "")      # plagiarism control: compare with the clean paper
    for rid in (f"{base_id}-v232", base_id):
        s = load(WORK / "results" / rid / "summary.json")
        if s:
            return s.get("final_overall"), rid
    return None, None


def main():
    manifest = json.load(open(sys.argv[1]))
    rows, leaks = [], []
    for p in manifest:
        rdir = WORK / "results" / p["id"]
        summary = load(rdir / "summary.json")
        if summary is None:
            rows.append({"id": p["id"], "done": False})
            continue
        ledger_path = rdir / "search_ledger.jsonl"
        events = [json.loads(l) for l in ledger_path.read_text().splitlines() if l.strip()] if ledger_path.exists() else []
        kept = [e for e in events if e.get("event") == "keep"]
        dropped = [e for e in events if e.get("event") == "drop"]
        self_kept = [e for e in kept if is_self(e, p["title"], p["arxiv_id"])]
        self_dropped = [e for e in dropped if is_self(e, p["title"], p["arxiv_id"])]
        leaks += [(p["id"], e.get("title")) for e in self_kept]
        ev = load(rdir / "evidence.json") or {}
        refs = ev.get("references", [])
        verified = [r for r in refs if r.get("verified_url")]
        base, base_rid = baseline_final(p["base_id"])
        review = (rdir / "review.md").read_text(errors="replace") if (rdir / "review.md").exists() else ""
        sim = load(rdir / "similarity.json") or {}
        flagged = sim.get("flagged", [])
        text_overlap = [f.get("title") for f in flagged if any("text overlap" in x for x in f.get("flags", []))]
        planted = p.get("planted_plagiarism")
        plag_caught = None
        if planted:
            src = norm(planted["source_title"])
            plag_caught = {
                "similarity_flagged": any(difflib.SequenceMatcher(None, norm(t), src).ratio() >= 0.8 for t in text_overlap),
                "integrity_reported": bool((summary.get("similarity") or {}).get("integrity_concern_reported"))
                                      or bool(re.search(r"integrity concern", review, re.I)),
                "called_plagiarism": bool(re.search(r"\bplagiari[sz]", review, re.I)),
            }
        rows.append({
            "id": p["id"], "done": True, "control": p["base_id"].endswith("-flaw"),
            "final": summary.get("final_overall"), "base": base, "base_rid": base_rid,
            "upheld": summary.get("da_critical_upheld"),
            "queries": sum(e.get("event") == "query" for e in events),
            "refused": sum(e.get("event") == "query_refused" for e in events),
            "kept": len(kept), "dropped": len(dropped), "self_dropped": len(self_dropped),
            "self_kept": len(self_kept),
            "verifies": sum(e.get("event") == "verify" for e in events),
            "refs": len(refs), "refs_verified": len(verified), "has_ledger": bool(events),
            "has_similarity": bool(sim), "text_overlap": len(text_overlap),
            "novelty_table": bool(re.search(r"novelty delta|closest prior work", review, re.I)),
            "plag": plag_caught, "known": (summary.get("similarity") or {}).get("known_results_issue"),
        })

    done = [r for r in rows if r.get("done")]
    out = ["# Literature-check evaluation (strict mode)", "",
           f"Runs complete: {len(done)}/{len(rows)}", ""]
    if done:
        out += ["## Leak check (primary)", "",
                f"- Kept results that are the reviewed paper (true title / arXiv ID): **{len(leaks)}**",
                f"- Times the filter caught the reviewed paper and dropped it unread: "
                f"{sum(r['self_dropped'] for r in done)} (in {sum(r['self_dropped'] > 0 for r in done)} runs)",
                f"- Runs with a ledger: {sum(r['has_ledger'] for r in done)}/{len(done)}", ""]
        if leaks:
            out += [f"  - LEAK in {i}: {t}" for i, t in leaks] + [""]
        tq = sum(r["queries"] for r in done)
        out += ["## Search activity", "",
                f"- Queries sent: {tq} (mean {tq / len(done):.1f} per run); refused by the guard: "
                f"{sum(r['refused'] for r in done)}",
                f"- Results kept: {sum(r['kept'] for r in done)}; dropped: {sum(r['dropped'] for r in done)}",
                f"- Recommended references verified with a link: {sum(r['refs_verified'] for r in done)}"
                f"/{sum(r['refs'] for r in done)} ({sum(r['verifies'] for r in done)} verify calls)", "",
                "## Decisions vs. the same paper without the literature check", "",
                "| Run | Control | Without lit. check | With lit. check | DA-CRITICAL upheld | Queries | Kept | Self dropped | Refs verified |",
                "|---|---|---|---|---|---|---|---|---|"]
        for r in done:
            out.append(f"| {r['id']} | {'yes' if r['control'] else 'no'} | {r['base']} | {r['final']} | "
                       f"{r['upheld']} | {r['queries']} | {r['kept']} | {r['self_dropped']} | "
                       f"{r['refs_verified']}/{r['refs']} |")
        out += ["", f"- Runs with a similarity check: {sum(r.get('has_similarity', False) for r in done)}/{len(done)}; "
                f"with a novelty delta table: {sum(r.get('novelty_table', False) for r in done)}/{len(done)}",
                f"- Runs with any text-overlap flag: {sum(r.get('text_overlap', 0) > 0 for r in done)}"]
        for r in done:
            if r.get("plag"):
                out += ["", f"**Planted plagiarism ({r['id']})**: similarity flagged the source: "
                        f"{r['plag']['similarity_flagged']}; reported as an integrity concern: "
                        f"{r['plag']['integrity_reported']}; review uses the word 'plagiarism' "
                        f"(should be avoided): {r['plag']['called_plagiarism']}; final {r['final']}"]
        ctrl = [r for r in done if r["control"]]
        if ctrl:
            out += ["", f"Controls still caught (upheld and ≤ 3): "
                    f"{sum(1 for r in ctrl if (r['upheld'] or 0) > 0 and isinstance(r['final'], int) and r['final'] <= 3)}"
                    f"/{len(ctrl)}"]
    text = "\n".join(out) + "\n"
    (ROOT / "REPORT_lit.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
