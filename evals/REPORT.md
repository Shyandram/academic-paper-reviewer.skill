# Evaluation Report: Recently Accepted Papers

Papers sampled: 30 · complete runs: 30

## Decisions (reference only)

All sampled papers were accepted at their venue. Agreement with that outcome is reported **for reference, not as a target**: the skill is not tuned to reproduce venue decisions. The primary checks are grounding, the planted-flaw controls and internal consistency (below).

- Accept-side (Overall ≥ 4): **16/30 = 53%** (95% CI 36%–70%)
- Overall distribution: 6: 0, 5: 0, 4: 16, 3: 14, 2: 0, 1: 0
- Mean Overall: 3.53; mean panel composite: 60.1

| Slice | n | Accept-side | Mean Overall |
|---|---|---|---|
| venue: cvpr | 10 | 4/10 | 3.40 |
| venue: eccv | 10 | 7/10 | 3.70 |
| venue: iclr | 10 | 5/10 | 3.50 |
| topic: 3d | 3 | 2/3 | 3.67 |
| topic: detseg | 3 | 1/3 | 3.33 |
| topic: efficient | 3 | 2/3 | 3.67 |
| topic: generation | 3 | 1/3 | 3.33 |
| topic: lowlevel | 3 | 1/3 | 3.33 |
| topic: medical | 3 | 1/3 | 3.33 |
| topic: representation | 3 | 2/3 | 3.67 |
| topic: robustness | 3 | 2/3 | 3.67 |
| topic: video | 3 | 2/3 | 3.67 |
| topic: vlm | 3 | 2/3 | 3.67 |

## BEFORE vs AFTER (EIC weighting)

- Mean composite BEFORE (confidence-weighted): 60.5
- Mean composite AFTER (EIC-weighted): 60.1
- Mean |AFTER − BEFORE|: 0.4
- Decisions departing from the AFTER band: 4/30
- Reviewers weighted ≠ 1.0 by the EIC: 73/150

## Devil's Advocate and decision mechanics

- Papers with ≥ 1 DA-CRITICAL raised: 11/30 (37%); upheld: 0/30 (0%)
- Decisions lowered by the DA cap: 0/30
- Papers with consistency warnings: 0/30
- Final exceeding the ceiling (rule violation): 0
- Papers the reviewer recognized from prior knowledge: 0/30
- Prompt injections found in papers: 0

## Grounding (hallucination checks)

| Check | Checked | Not found in paper | Rate |
|---|---|---|---|
| Cited locations (tables, figures, sections, equations) | 1101 | 48 | 4% |
| Quoted phrases | 778 | 9 | 1% |
| Quoted numbers | 842 | 2 | 0% |

Numbers the reviewers recomputed themselves (excluded above; spot-checked by hand): 525.

Recommended references: 186 total, 38 marked `[verify]`. A reference missing from arXiv is not necessarily fabricated (not every paper is on arXiv); those are listed in the detail file for manual checking.

## Structure

- Runs with all required sections: 30/30
- Median review length: 10214 words

## Planted-flaw controls

Accepted papers with one inserted sentence admitting a fatal evaluation flaw (hyperparameters tuned on the test set, or test split merged into training). A calibrated reviewer must catch it and decide ≤ 3.

- Flaw mentioned in the review: 6/6
- Flaw raised as DA-CRITICAL: 2/6
- Decision ≤ 3: 5/6

| Control | Flaw | Mentioned | DA-CRITICAL | Upheld by EIC | Final |
|---|---|---|---|---|---|
| cvpr-detseg | test-tuning | yes | no | no | 3 |
| cvpr-lowlevel | train-on-test | yes | yes | yes | 3 |
| eccv-3d | test-tuning | yes | no | no | 3 |
| eccv-video | train-on-test | yes | no | no | 3 |
| iclr-video | test-tuning | yes | no | no | 4 |
| iclr-efficient | train-on-test | yes | yes | yes | 3 |

