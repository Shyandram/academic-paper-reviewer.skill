# Evaluation Report: Recently Accepted Papers

Papers sampled: 16 · complete runs: 13

## Decisions (reference only)

All sampled papers were accepted at their venue. Agreement with that outcome is reported **for reference, not as a target**: the skill is not tuned to reproduce venue decisions. The primary checks are grounding, the planted-flaw controls and internal consistency (below).

- Accept-side (Overall ≥ 4): **6/13 = 46%** (95% CI 23%–71%)
- Overall distribution: 6: 0, 5: 0, 4: 6, 3: 7, 2: 0, 1: 0
- Mean Overall: 3.46; mean panel composite: 58.9

| Slice | n | Accept-side | Mean Overall |
|---|---|---|---|
| venue: cvpr | 10 | 4/10 | 3.40 |
| venue: eccv | 2 | 1/2 | 3.50 |
| venue: iclr | 1 | 1/1 | 4.00 |
| topic: 3d | 1 | 1/1 | 4.00 |
| topic: detseg | 2 | 1/2 | 3.50 |
| topic: efficient | 1 | 0/1 | 3.00 |
| topic: generation | 2 | 1/2 | 3.50 |
| topic: lowlevel | 1 | 0/1 | 3.00 |
| topic: medical | 2 | 0/2 | 3.00 |
| topic: representation | 1 | 0/1 | 3.00 |
| topic: robustness | 1 | 1/1 | 4.00 |
| topic: video | 1 | 1/1 | 4.00 |
| topic: vlm | 1 | 1/1 | 4.00 |

## BEFORE vs AFTER (EIC weighting)

- Mean composite BEFORE (confidence-weighted): 59.4
- Mean composite AFTER (EIC-weighted): 58.9
- Mean |AFTER − BEFORE|: 0.5
- Decisions departing from the AFTER band: 1/13
- Reviewers weighted ≠ 1.0 by the EIC: 31/65

## Devil's Advocate and decision mechanics

- Papers with ≥ 1 DA-CRITICAL raised: 3/13 (23%); upheld: 0/13 (0%)
- Decisions lowered by the DA cap: 0/13
- Papers with consistency warnings: 0/13
- Final exceeding the ceiling (rule violation): 0
- Papers the reviewer recognized from prior knowledge: 0/13
- Prompt injections found in papers: 0

## Grounding (hallucination checks)

| Check | Checked | Not found in paper | Rate |
|---|---|---|---|
| Cited locations (tables, figures, sections, equations) | 463 | 6 | 1% |
| Quoted phrases | 272 | 0 | 0% |
| Quoted numbers | 476 | 0 | 0% |

Numbers the reviewers recomputed themselves (excluded above; spot-checked by hand): 199.

Recommended references: 82 total, 19 marked `[verify]`. A reference missing from arXiv is not necessarily fabricated (not every paper is on arXiv); those are listed in the detail file for manual checking.

## Structure

- Runs with all required sections: 13/13
- Median review length: 9978 words

## Planted-flaw controls

Accepted papers with one inserted sentence admitting a fatal evaluation flaw (hyperparameters tuned on the test set, or test split merged into training). A calibrated reviewer must catch it and decide ≤ 3.

- Flaw mentioned in the review: 1/1
- Flaw raised as DA-CRITICAL: 0/1
- Decision ≤ 3: 1/1

| Control | Flaw | Mentioned | DA-CRITICAL | Upheld by EIC | Final |
|---|---|---|---|---|---|
| cvpr-detseg | test-tuning | yes | no | no | 3 |

