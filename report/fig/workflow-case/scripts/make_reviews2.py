import json, hashlib, sys
REV = sys.argv[1]; G4DEC = sys.argv[2] if len(sys.argv) > 2 else "pass"
from pathlib import Path
D = Path("/home/user/figcase/out")
sha = lambda p: hashlib.sha256((D / p).read_bytes()).hexdigest()
(D / "design.md").write_text("""# apr_workflow design

- Width 162 mm (the report's A4 text width; r00 assumed 170 mm), aspect about 1.9; paper-clean theme (8 pt body, 7 pt minimum, Okabe-Ito roles).
- Reading order left to right: Manuscript -> Phase 0 (Integrity scan, Field analysis -> Reviewer packet) -> Five reviewers
  (group) -> Literature check -> Report check -> Editor-in-Chief (hero, the largest bold frame) -> Decision letter /
  Score script -> Venue forms.
- Roles: input blue; preparation sky; reviewers green; checks amber; EIC vermilion; deterministic script white; outputs
  pink; optional grey and muted inside a dotted "Optional" band.
- Arrow grammar: document flow solid black; integrity findings a thin labelled vermilion parameter_control arrow that
  passes over the reviewers to the EIC, showing that the reviewers never see them.
- The packet and the literature check are tall blocks spanning the five reviewers so the fan-out and fan-in are parallel.
- Caption carries phase numbers, quality weighting, the 11 venues, the self-exclusion of the literature search, and that
  the Gap Scout never changes the review.
""")
PL = sha("plan.json")
def review(gate, dims, hashes, extra_lim=()):
    ws = 100 * sum(s / 5 for _, s, _ in dims) / len(dims)
    return {"schema": "StageReview@2", "figure_id": "apr_workflow", "gate": gate, "revision": int(REV[1:]), "reviewer_mode": "same_context",
            "rubric_version": "paper-figure/SupervisorRubric@2", "artifact_hashes": hashes, "plan_sha256": PL,
            "dimensions": [{"name": n, "weight": 1, "score": s, "evidence": [e], "artifact_uri": list(hashes)[0]} for n, s, e in dims],
            "weighted_score_100": round(ws, 1), "coverage": 1.0, "hard_blockers": [], "defects": [], "decision": "pass",
            "limitations": ["same_context review by the generating session; not an independent reviewer"] + list(extra_lim)}
src = "inputs/SKILL.md"
R = {}
R["G0"] = review("G0", [("source_allowlist", 5, "the only source is inputs/SKILL.md (the skill's own spec, user_architecture); the previous Figure 1 was not opened"),
                        ("source_integrity", 5, "sha256 of inputs/SKILL.md recorded in plan.sources and matches the file"),
                        ("equation_coverage", 5, "the source defines no equations for the workflow; none were added"),
                        ("reference_selection", 4, "sample_ids is empty; no unlisted samples were used; style comes only from the paper-clean theme")],
                 {"task_packet.json": sha("task_packet.json"), src: sha(src), "plan.json": PL})
R["G1"] = review("G1", [("topology_or_argument", 5, "order Phase 0 -> Phase 1 -> 1.5 -> 1.6 -> Phase 2 follows 'Order: Phase 1 -> Phase 1.5 -> Phase 1.6 -> Phase 2' in SKILL.md"),
                        ("object_edge_semantics", 4, "findings go to the EIC alone (Hard Rule 9); reviewers read the redacted copy and paper memory; 'Reviewer packet' is an inferred name, recorded in inferred_details"),
                        ("training_inference_scope", 5, "no training/inference split exists; every object is scope both and no such claim is made"),
                        ("claim_scope", 5, "the Gap Scout is outside the review band and has no edge into the review, matching 'never changes a report, a score ... or the decision'")],
                 {"plan.json": PL})
R["G2"] = review("G2", [("communication_hierarchy", 5, "the EIC is the hero (bold, thick frame); reviewers grouped; optional part muted in a dotted band"),
                        ("reading_order", 5, "single left-to-right pass; outputs on the right"),
                        ("role_consistency", 4, "one colour per role, Okabe-Ito; the two checks share amber"),
                        ("arrow_layout", 4, "fan-out and fan-in run in parallel lanes; one long findings arrow over the top")],
                 {"design.md": sha("design.md"), "plan.json": PL})
R["G3"] = review("G3", [("plan_spec_fidelity", 5, "validate_artifact spec --plan passes; 17 nodes, 22 relations equal plan edges"),
                        ("backend_structure", 5, "compile_drawio: no router failures or overlaps; lint at 162 mm: 0 errors, 1 warning (label_tight, Venue forms 4.4 units), 0 crossings"),
                        ("editable_objects_or_prompt_constraints", 5, "native vertices and edges with data-plan-id; the group is a real container; validate_artifact figure --plan --spec passes"),
                        ("provenance_binding", 4, "spec.plan_sha256 and drawio maps bound; no required_labels declared")],
                 {f"spec.{REV}.json": sha(f"spec.{REV}.json"), f"figure.{REV}.drawio": sha(f"figure.{REV}.drawio"), "plan.json": PL},
                 ["prompt review waived by the packet (drawio backend only)"])
R["G4"] = review("G4", [("actual_scientific_fidelity", 5, f"viewed figure.{REV}.pdf at 300 dpi: every arrow ends on its plan target; findings arrow reaches only the EIC"),
                        ("publication_size_readability", 4, "min 7.20 pt at 162 mm (lint --pdf); 32 words; Venue forms text 4.4 units from its border; the tall Literature check block leaves empty space"),
                        ("routing_roles", 5, "no crossings or overlaps; typed arrows: solid flow, thin labelled vermilion control arrow"),
                        ("evidence_visual_integrity", 5, "no data, photos or plots are drawn"),
                        ("export_fidelity", 5, "native draw.io 32.4.1 export; PDF fonts embedded (Liberation Sans); PNG and SVG from the same file")],
                 {f"figure.{REV}.pdf": sha(f"figure.{REV}.pdf"), f"figure.{REV}.drawio": sha(f"figure.{REV}.drawio"), f"figure.{REV}.png": sha(f"figure.{REV}.png"), f"figure.{REV}.svg": sha(f"figure.{REV}.svg"), "plan.json": PL},
                 ["native exporter run through a host shim (xvfb-run, --no-sandbox) because the container runs as root", "r00 was sized for 170 mm; at the report text width (162 mm) its band title printed at 6.86 pt; r01 recompiles the plan at 162 mm", "r02 (wider output blocks) regressed: Decision letter came within 1.6 units of its border; with the repair budget spent, r01 is delivered"])
(D / "reviews").mkdir(exist_ok=True)
for g, r in R.items(): (D / "reviews" / f"{g}.{REV}.json").write_text(json.dumps(r, indent=1) + "\n")
outs, lims = {}, []
for f in ("pdf", "png", "svg"):
    b = json.loads((D / f"render.{REV}.{f}.json").read_text())
    for o in b["outputs"]: outs[o["uri"]] = dict(o, verification=o.get("verification"))
    lims += [l for l in b["limitations"] if not l.startswith("G4 still requires")]
base = json.loads((D / f"render.{REV}.pdf.json").read_text())
base.update(outputs=list(outs.values()), limitations=sorted(set(lims)) + ["r02 regressed (label_tight 1.6 units on Decision letter) and is not delivered; repair budget (2) spent", "native export ran through /home/user/figcase/drawio-wrap.sh (root container: --no-sandbox, xvfb)"], preview_status="verified", backend_status="completed")
man = {"schema": "RenderManifest@2", "figure_id": "apr_workflow", "plan_sha256": PL, "spec_sha256": sha(f"spec.{REV}.json"), "repair_count": int(REV[1:]),
       "deliver_status": "complete", "backends": [base], "review_hashes": {f"reviews/{g}.{REV}.json": sha(f"reviews/{g}.{REV}.json") for g in R},
       "provenance": {"status": "ordinary", "excluded_from_clean_aggregate": False, "input_hashes": {src: sha(src)},
                      "parent_artifact_hashes": {"plan.json": PL, f"spec.{REV}.json": sha(f"spec.{REV}.json")}, "source_coverage": [],
                      "recorded_at": json.loads((D / "plan.json").read_text())["provenance"]["recorded_at"]}}
(D / "render.manifest.json").write_text(json.dumps(man, indent=1) + "\n")
print(json.dumps([(o["uri"], o["kind"], o["verification"]) for o in base["outputs"]]))
