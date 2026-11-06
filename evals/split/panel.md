## This phase: Phase 0 and Phase 1 (one context, as in the single pipeline)

You run the panel up to the end of Phase 1. The literature check and the report check
(Phases 1.5 and 1.6) run afterwards in a separate, fresh context, and this context is then
resumed for Phase 2. Do not run Phases 1.5, 1.6 or 2 now.

Read `{SKILL}/SKILL.md` first, then the files it lists for full mode up to Phase 1: the agents
(not `report_checker_agent.md`, `editorial_synthesizer_agent.md` or `eic_agent.md` yet),
`references/quality_rubrics.md`, `references/review_criteria_framework.md`,
`references/statistical_reporting_standards.md`, `references/cv_review_checklist.md`,
`references/error_audit.md`, `references/venue_profiles.md` and
`templates/peer_review_report_template.md`. Then read the complete paper: `{PAPER}`.

**Phase 0.** Run, in this order:
1. `python3 {SKILL}/scripts/integrity_scan.py --paper {PAPER} --json --redact {RES}/phase0/reviewer_copy.txt > {RES}/phase0/integrity.json`
   The findings are for the EIC only. Do not mention them in any report.
2. If the literature check is not `off`:
   `python3 {SKILL}/scripts/related_search.py fingerprint --paper {PAPER} --out {RES}/phase0/fingerprint.json`,
   then complete the fingerprint as `references/literature_search.md` describes (title, method
   names, identifiers, distinctive phrases, cutoff date {CUTOFF}).

Write to `{RES}/phase0/`: `card.md` (the Reviewer Configuration Card), `paper_memory.md` (Section 3
of `error_audit.md`; facts only) and
`panel.json`: `{"paper_type": "<empirical|theoretical|dataset|system|benchmark|analysis|position>", "field": "...", "venue_tier": "...", "recognized": false}`.

**Phase 1.** Run the four reviewers one after another yourself, from the redacted copy
`{COPY}` and the paper memory, as the skill instructs; do not launch subagents. Keep each
reviewer independent. Before scoring, state the paper's **pool position**, then score within
the matching band. For each reviewer `<R1|R2|R3|R4>` write to `{RES}/reports/<role>/`:
1. `report.md`: the complete report (template). The Devil's Advocate is not a reviewer: the
   Report Checker runs it later, in a fresh context.
2. `scores.json`:
   ```json
   {
     "role": "<R1 (Meth.)|R2 (Domain)|R3 (Persp.)|R4 (Gen.)>",
     "confidence": 1-5,
     "overall": 1-6,
     "pool_position": 0-100,
     "scores": {"technical_rigor": 0-100, "clarity": 0-100, "novelty": 0-100, "significance": 0-100,
                "experimental_validation": 0-100, "reproducibility": 0-100, "ethics": 0-100},
     "claims": ["C1", "C2"],
     "recognized": false
   }
   ```
   Numbers as numbers. Reviewer 1 lists the full claim-to-evidence map in `claims`.

Reply with one line: the four Overall ratings.
