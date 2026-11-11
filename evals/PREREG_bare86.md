# Pre-registration: bare-model control on the 86-paper ICLR 2026 set

Written 2026-11-11, before the run. The run's result goes into `REPORT_iclr2026_pilots.md`; this file is not edited afterwards except under "Amendments".

## Question

How much of the 2.10.1 skill's agreement with human reviewers comes from the skill, and how much from the model alone? The skill's numbers on the 86 balanced papers (Sonnet, high effort) are: Spearman +0.47 against the mean human rating, AUC 0.64 for acceptance, human-issue hit rate 0.46, AI issues matching a human issue 0.26.

## Design

- **Papers:** the same 86 papers (`evals/work/full_metrics/splits.json`, 45 train / 41 test), original blinded text, no seeds.
- **Control:** `evals/bare_prompt.md`, same model and effort as the skill runs, the same evaluation rules (untrusted text, no web), one context, no skill files in the workspace. The request is only "Review this paper. Target venue: ICLR." and the ICLR form (rating 0/2/4/6/8/10, confidence 1-5, top concerns).
- **Runner:** GitHub Actions, `claude` runner, API key from the repository secret, per-paper cap 1 USD. The 3-paper seeded bare run cost 0.18 USD for one paper, so the whole set should cost about 15-25 USD.
- **One run per paper.** No reruns except for a paper whose job failed before writing `summary.json`; any such rerun is listed.

## Measures

Primary, on all 86 and on the 41 test papers:
1. Spearman of the bare rating against the mean human rating, and AUC for acceptance.
2. The paired-bootstrap 95% CI (2000 resamples of papers, seed 0, `offline_signals.py` method) of the Spearman difference skill panel rating minus bare rating.

Secondary:
3. Tie rate of the bare rating (share of paper pairs with equal ratings). A single integer rating ties often, and arXiv 2610.19339 finds that most of the ranking gain from averaging comes from breaking ties; the skill's panel mean of five reviewers is continuous. To separate "more reviews" from "the skill", we also report the bare rating's Spearman on the untied pairs only (Kendall tau-b) next to the skill's.
4. Human-issue overlap of the bare top concerns and weaknesses, annotated with the same `issue_overlap_prompt.md` and `issue_overlap.py` as the skill's (hit rate, AI precision), run afterwards as a separate step.

## Predictions (stated before the run)

- Bare Spearman between +0.25 and +0.45 and AUC between 0.58 and 0.68, in the range the arXiv study reports for single AI reviews (Spearman 0.35-0.41, AUC 0.65-0.71 on its 200 papers).
- The skill is at least as good as bare on Spearman, but with 86 papers the CI of the difference will probably include 0. A CI that excludes 0 in either direction is a finding; a CI that includes 0 is not evidence that the skill adds nothing.
- Bare ties on at least 30% of paper pairs.
- Issue overlap: bare hit rate lower than the skill's 0.46 (it writes fewer issues) and AI precision near or above the skill's 0.26 (fewer, more central issues).

## What we will not do

- Pick the better of several bare runs, or change the prompt after seeing results.
- Tune any skill threshold on these results without a held-out check.
- Let ICLR ground truth reach the reviewer: the prepare job ships `blinded.txt` only, and the review job deletes everything but the paper and the prompt.
