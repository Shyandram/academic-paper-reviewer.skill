# Evaluation Report: Recently Accepted Papers

Papers sampled: 3 · complete runs: 3

## Decisions (reference only)

All sampled papers were accepted at their venue. Agreement with that outcome is reported **for reference, not as a target**: the skill is not tuned to reproduce venue decisions. The primary checks are grounding, the planted-flaw controls and internal consistency (below).

- Accept-side (Overall ≥ 4): **0/3 = 0%** (95% CI 0%–56%)
- Overall distribution: 6: 0, 5: 0, 4: 0, 3: 3, 2: 0, 1: 0
- Mean Overall: 3.00; mean panel composite: 58.3

| Slice | n | Accept-side | Mean Overall |
|---|---|---|---|
| venue: cvpr | 2 | 0/2 | 3.00 |
| venue: iclr | 1 | 0/1 | 3.00 |
| topic: 3d | 1 | 0/1 | 3.00 |
| topic: detseg | 1 | 0/1 | 3.00 |
| topic: medical | 1 | 0/1 | 3.00 |

## BEFORE vs AFTER (EIC weighting)

- Mean composite BEFORE (confidence-weighted): 58.8
- Mean composite AFTER (EIC-weighted): 58.3
- Mean |AFTER − BEFORE|: 0.5
- Decisions departing from the AFTER band: 0/3
- Reviewers weighted ≠ 1.0 by the EIC: 6/15

## Devil's Advocate and decision mechanics

- Papers with ≥ 1 DA-CRITICAL raised: 0/3 (0%); upheld: 0/3 (0%)
- Decisions lowered by the DA cap: 0/3
- Papers with consistency warnings: 0/3
- Final exceeding the ceiling (rule violation): 0
- Papers the reviewer recognized from prior knowledge: 0/3
- Prompt injections found in papers: 0

## Grounding (hallucination checks)

| Check | Checked | Not found in paper | Rate |
|---|---|---|---|
| Cited locations (tables, figures, sections, equations) | 124 | 5 | 4% |
| Quoted phrases | 63 | 0 | 0% |
| Quoted numbers | 121 | 1 | 1% |

Numbers the reviewers recomputed themselves (excluded above; spot-checked by hand): 66.

Recommended references: 19 total, 4 marked `[verify]`. A reference missing from arXiv is not necessarily fabricated (not every paper is on arXiv); those are listed in the detail file for manual checking.

## Structure

- Runs with all required sections: 3/3
- Median review length: 9663 words

## Planted-flaw controls

Accepted papers with one inserted sentence admitting a fatal evaluation flaw (hyperparameters tuned on the test set, or test split merged into training). A calibrated reviewer must catch it and decide ≤ 3.

- Flaw mentioned in the review: 1/1
- Flaw raised as DA-CRITICAL: 1/1
- Decision ≤ 3: 1/1

| Control | Flaw | Mentioned | DA-CRITICAL | Upheld by EIC | Final |
|---|---|---|---|---|---|
| cvpr-detseg | test-tuning | yes | yes | yes | 3 |

