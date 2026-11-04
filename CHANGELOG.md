# Changelog

## 2.3.1 (2026-11-04)
- **Fix: EIC weights were anchored on the example.** In 9 of 10 runs on v2.3, the EIC copied `scripts/example_scores.json`'s weights (R1 1.25, R3 0.75) instead of judging each paper. The format example now uses neutral weights (all 1.0), and the CV example's illustrative weights moved to `examples/cv_example_scores.json`. The EIC instructions now say to start every reviewer at 1.0, move a weight only for a paper-specific verified reason, and never weight by role.
- **Fix:** the target-venue label always equals the EIC decision, and venue shifts are ignored when a band edge is crossed by less than 2 points.

## 2.3 (2026-11-04)
- **The decision starts from the reviewers' recommendations.** The starting point is the EIC-weighted mean of the reviewers' Overall ratings (confidence × EIC quality weight, rounded half up). The 0–100 composite becomes a cross-check: the script flags it when its band differs, and the EIC must say which signal it trusts. (On v2.2, a CVPR Highlight rated 3/4/4/4/3 got Borderline Reject because its composite was 59.4, under the cutoff of 60.)
- **Two score lists.** Official = the plain mean of the raw ratings and scores (what authors see, never modified). EIC assessment = internal and weighted, which can be higher or lower.
- **`--final N`** renders venue labels from the EIC's actual decision. The target venue (the first `--venue`) always shows the decision itself. Other venues shift only for real bar or emphasis differences, never for a band edge crossed by less than 2 points.
- **New-task papers** are judged on the value of the task and the evidence, not on technical novelty alone.

## 2.2 (2026-11-04)

Calibration overhaul, driven by an evaluation on recently accepted papers. Version 2.1.2 gave 7 of 7 accepted ICLR/CVPR/ECCV papers *Borderline Reject*. In every case the Devil's Advocate raised a CRITICAL issue and it was upheld. See `evals/`.

### Changed
- **The EIC is now the meta-reviewer (area chair), not a reviewer.** It reads all five reviews first, then reads the paper briefly, verifying every decisive point. It weights each reviewer (0.5–1.5) by review quality, rules on DA-CRITICAL issues and makes the final decision.
- **New Reviewer 4 (Generalist)** keeps the panel at five: the typical committee member, responsible for venue fit and Clarity & Presentation.
- **BEFORE/AFTER scores.** `aggregate_scores.py` reports a confidence-weighted BEFORE score and an EIC-weighted AFTER score (`eic_weight` per reviewer), plus a reviewer-weight table.
- **Decision ceiling = DA cap only.** The composite band is a guideline the EIC may depart from, with a reason, in either direction.
- **Strict DA-CRITICAL criteria.** A new test asks whether the issue alone would make the paper unpublishable. An explicit list covers issues that are never critical on their own (single runs, a missing baseline, overclaimed wording, partly controlled confounds, missing details), plus a base rate: most accepted papers have none. The synthesizer's "default to uphold" rule is removed.
- **Venue anchors** in the rubrics: 62–69 for a typical accepted paper, 70–80 for a solid accept. Supplementary material referenced but not provided counts as unverified, not missing. Never tune scores to silence a consistency warning.
- The Synthesizer is now the EIC's assistant: it prepares the issue map and the BEFORE score, then assembles the package. It no longer decides.

## 2.1.2 (2026-11-04)
- AAAI now uses its 1–10 rating scale, confirmed by the maintainer: 10 Very strong accept … 6 Borderline accept · 5 Borderline reject · 4 Weak reject … 1 Very strong reject.

## 2.1.1 (2026-10-20)
- CVPR, ICCV and ECCV are now marked as using the confirmed 6-point rating scale (new `confirmed` status). The label wording still follows the ICCV 2025 reports.

## 2.1 (2026-10-15)

### Added
- **Venue-aware scoring for 11 venues**: CVPR, ICCV, ECCV, NeurIPS, ICLR, ICML, AAAI, ACM Multimedia, TMLR, IEEE TPAMI and IEEE TIP. `scripts/venues.json` holds each venue's emphasis weights, bar offset, scale and form fields.
- `aggregate_scores.py --venue <key>` / `--all-venues` produces the venue's own scores (ICLR sub-scores and rating, NeurIPS sub-scores, ICML 1–5, TMLR Yes/No criteria, IEEE journal recommendations) and a Cross-Venue Outlook with bands before and after the DA cap.
- A verification status for every venue scale (official / secondary / assumed / unpublished), with sources in `references/venue_profiles.md`.
- Venue-specific rules wired into the workflow: ECCV contribution types and "not beating SOTA is not grounds for rejection", the ACM MM multimedia-scope gate, AAAI Phase-1 risk, the TPAMI conference-extension check, and TMLR's correctness-over-novelty criteria.
- `compare venues` and `venue format` modifiers; a Cross-Venue Outlook section in the decision template and the CV example; tests for venue views.

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
