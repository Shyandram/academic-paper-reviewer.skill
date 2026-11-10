import json, hashlib, datetime
from pathlib import Path
D = Path("/home/user/figcase"); out = D / "out"; out.mkdir(exist_ok=True)
src_sha = hashlib.sha256((out / "inputs/SKILL.md").read_bytes()).hexdigest()
NOW = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
S = "src_skill"
sources = [{"id": S, "kind": "user_spec", "role": "method",
            "locator": {"uri": "inputs/SKILL.md", "span": "Full Mode Workflow; Post-Review Analysis; Hard Rule 9"},
            "sha256": src_sha, "provenance_status": "ordinary", "integrity": "clean"}]
def n(i, label, role, typ="module", status="stated", unc=None):
    return {"id": i, "label": label, "type": typ, "role": role, "scope": "both", "evidence_ids": [S],
            "status": status, "uncertainty": unc}
def e(i, a, b, meaning, typ="feature", **kw):
    d = {"id": i, "from": a, "to": b, "type": typ, "scope": "both", "meaning": meaning, "evidence_ids": [S]}
    d.update(kw); return d
nodes = [n("paper", "Manuscript", "input", "input"),
         n("field", "Field analysis", "prep"), n("scan", "Integrity scan", "prep"),
         n("packet", "Reviewer packet", "prep", "data"),
         n("r1", "Methodology", "reviewer"), n("r2", "Domain", "reviewer"), n("r3", "Perspective", "reviewer"),
         n("r4", "Generalist", "reviewer"), n("da", "Devil's Advocate", "reviewer"),
         n("lit", "Literature check", "check"), n("chk", "Report check", "check"),
         n("eic", "Editor-in-Chief", "editor"), n("agg", "Score script", "script"),
         n("dec", "Decision letter", "output", "output"), n("venue", "Venue forms", "output", "output"),
         n("gap", "Gap Scout", "optional"), n("gapout", "Concern checklist", "optional", "output")]
edges = [e("e_pf", "paper", "field", "the manuscript is analysed for field, venue and reviewer configuration"),
         e("e_ps", "paper", "scan", "the manuscript text is scanned for reviewer-directed text"),
         e("e_fp", "field", "packet", "configuration card and factual paper memory"),
         e("e_sp", "scan", "packet", "redacted reviewers' copy"),
         *[e("e_p" + r, "packet", r, "each reviewer gets the packet and its own role file, not others' reports") for r in ("r1", "r2", "r3", "r4", "da")],
         *[e("e_" + r + "l", r, "lit", "the drafted report goes to the literature check") for r in ("r1", "r2", "r3", "r4", "da")],
         e("e_lc", "lit", "chk", "reports plus literature addendum go to the report check"),
         e("e_ce", "chk", "eic", "checked reports reach the EIC in Phase 2"),
         e("e_se", "scan", "eic", "integrity findings go to the EIC alone", "parameter_control", label="findings"),
         e("e_ed", "eic", "dec", "the EIC makes the decision and the revision roadmap"),
         e("e_ea", "eic", "agg", "scores and reviewer weights are aggregated by a deterministic script"),
         e("e_av", "agg", "venue", "aggregated scores are translated into venue forms"),
         e("e_pg", "paper", "gap", "the optional Gap Scout reads only the paper, after the review"),
         e("e_gg", "gap", "gapout", "it lists concrete concerns as a checklist")]
plan = {"schema": "PaperFigurePlan@2", "figure_id": "apr_workflow", "figure_type": "architecture",
  "communication_goal": "Show the full-mode review: two preparation steps feed a packet to five independent reviewers; their reports pass a literature check and a report check before the Editor-in-Chief, who decides; a script turns scores into venue forms; the Gap Scout is optional and outside the review.",
  "hero_mechanism": "eic", "sources": sources,
  "graph": {"nodes": nodes, "edges": edges,
            "groups": [{"id": "g_rev", "label": "Five reviewers", "members": ["r1", "r2", "r3", "r4", "da"]}],
            "shared_weights": []},
  "required_labels": [], "inferred_details": ["'Reviewer packet' names the bundle Phase 0 hands each reviewer (configuration card, paper memory, redacted copy); SKILL.md describes the contents, not this name."],
  "unknown_details": [], "selected_sample_reference_ids": [], "reference_transfer": [],
  "layout": {"target_width_mm": 162, "aspect_ratio": 2.2, "reading_order": ["paper", "field", "scan", "packet", "r1", "lit", "chk", "eic", "dec", "agg", "venue", "gap"],
             "regions": [], "arrow_grammar": {"feature": "solid", "parameter_control": "thin labeled"}, "style_roles": {},
             "caption_only_context": ["Phase numbers", "the EIC weights each review by quality", "11 venues", "the literature check cannot retrieve the paper under review"]},
  "forbidden_implications": ["reviewers see each other's reports", "the Gap Scout changes scores or the decision", "the scan changes scores"],
  "generation_prompt": "Left-to-right editorial pipeline diagram.",
  "provenance": {"status": "ordinary", "excluded_from_clean_aggregate": False, "input_hashes": {"inputs/SKILL.md": src_sha},
                 "parent_artifact_hashes": {}, "source_coverage": [], "recorded_at": NOW}}
(out / "plan.json").write_text(json.dumps(plan, indent=1, ensure_ascii=False) + "\n")
task = {"schema": "PaperFigureTask@2", "run_id": "apr-workflow-01", "input_mode": "user_architecture",
  "figure_type": "architecture", "requested_backends": ["drawio"], "plan_only": False, "sources": sources,
  "reference_policy": {"sample_ids": [], "style_selection": "confirmed", "style_profile": "paper-clean"},
  "output_dir": "out", "review": {"reviewer_mode": "same_context", "repair_limit": 2, "prompt_review": "waived"},
  "test_policy": {"held_out": False, "excluded_sources": ["previous Figure 1 of the technical report"], "allow_supplemental": False},
  "notes": "no skill-journal writes"}
(out / "task_packet.json").write_text(json.dumps(task, indent=1, ensure_ascii=False) + "\n")
