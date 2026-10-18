# Changelog

## 2.1 (2026-10-18)

- Added Codex project/personal installation with collision protection and an idempotent source link.
- Added runtime guidance for PDF extraction, permission-aware tools, offline use, and review artifacts.
- Made reviewer execution capability-aware with an explicit single-context fallback.
- Reduced repeated reference loading; proceed after panel configuration by default and offer coaching on request.
- Added installer regression tests and repository instructions for Codex maintenance.

## 2.0 (2026-10-15)

### Added
- **Rebuttal mode**: `agents/rebuttal_strategist_agent.md` and `templates/rebuttal_template.md` (one-page PDF and OpenReview layouts, triage tags, no-fabricated-results rule with `[TBD]` ledger).
- **Methodology-focus mode**, now fully specified: claim-to-evidence map, fairness-of-comparison audit, statistics audit, reproducibility checklist, prioritized fixes with compute estimates.
- **Submission Readiness Check** in quick mode (`references/submission_readiness_checklist.md`).
- `references/cv_review_checklist.md`: task-by-task expectations and confounds for CV/ML/multimodal papers.
- `references/venue_profiles.md`: review-form conventions, rebuttal formats and scale translation for CV/ML conferences and journals.
- `scripts/aggregate_scores.py`: deterministic confidence-weighted aggregation, paper-type composites, spread flags, DA-CRITICAL cap, consistency warnings; with tests.
- Composite weights for Benchmark/Survey, Analysis/Insight and Position papers. Review criteria for Position papers.
- 0–100 → 1–4 score mapping and calibration guidance. Field-norm calibration for statistical expectations in large-scale CV.
- Devil's Advocate: steelman step, numerical sanity check, visual-evidence check, explicit "no CRITICAL issues" statement, resolvability tag.
- Re-review: Reject outcome, response-letter verification table.
- Hard rules and a Responsible Use section: no fabricated references, fictional personas only, confidentiality reminder for assigned reviewers, integrity concerns reported factually.
- Input handling (PDF, LaTeX, partial manuscripts, arXiv) and output conventions (save to file, length).
- Repository: extracted source, `README.md` with installation, `tools/build_skill.py` (validate + deterministic packaging), unit tests.

### Changed
- One DA-CRITICAL rule everywhere: an upheld issue caps the decision at 4 if resolvable by clarification or minor additions, otherwise at 3.
- The synthesizer deduplicates issues and adds a CONSENSUS-2 class, plus rebuttal-feasibility and source IDs in the Roadmap.
- Confidence weight for level 1 (0.40) is now consistent between the synthesizer and the rubrics.
- The statistics reference replaces the APA 7th section with ML/CV reporting conventions, and adds paired-bootstrap/McNemar guidance and foundation-model evaluation requirements.
- Venue tiers updated (ICLR, TPAMI/IJCV, TMLR, MICCAI). Conference ↔ journal decision mapping added.

### Removed
- Off-domain example (Taiwan higher-education management) and its unverifiable references. The interdisciplinary example is replaced with a fictional medical-imaging case, and a fictional CV example is added. Examples no longer name real institutions as reviewer affiliations.
- Dangling references to skills and pipeline steps not shipped in this bundle (`academic-paper`, integrity verification).
- The duplicate response-letter template inside the editorial decision template; it now points to `templates/revision_response_template.md`.

## 1.4 (2026-03-16)
- Initial uploaded version.
