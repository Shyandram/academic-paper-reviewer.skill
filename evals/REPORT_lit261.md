# Literature-check evaluation (strict mode)

Runs complete: 5/5

## Leak check (primary)

- Kept results that are the reviewed paper (true title / arXiv ID): **0**
- Times the filter caught the reviewed paper and dropped it unread: 4 (in 3 runs)
- Runs with a ledger: 5/5

## Search activity

- Queries sent: 29 (mean 5.8 per run); refused by the guard: 0
- Results kept: 240; dropped: 105
- Recommended references verified with a link: 24/24 (25 verify calls)

## Decisions vs. the same paper without the literature check

| Run | Control | Without lit. check | With lit. check | DA-CRITICAL upheld | Queries | Kept | Self dropped | Refs verified |
|---|---|---|---|---|---|---|---|---|
| cvpr-3d-2607.02015-lit261 | no | 4 | 3 | 0 | 6 | 7 | 0 | 4/4 |
| eccv-vlm-2609.16847-lit261 | no | 4 | 3 | 1 | 6 | 95 | 1 | 5/5 |
| iclr-detseg-2604.14684-lit261 | no | 4 | 4 | 0 | 5 | 21 | 0 | 6/6 |
| eccv-generation-2609.28473-lit261 | no | 4 | 4 | 0 | 7 | 63 | 1 | 4/4 |
| eccv-3d-2607.26889-flaw-lit261 | yes | 3 | 3 | 1 | 5 | 54 | 2 | 5/5 |

- Runs with a similarity check: 5/5; with a novelty delta table: 5/5
- Runs with any text-overlap flag: 1

Controls still caught (upheld and ≤ 3): 1/1

## v2.6.1 vs. v2.6 (same 5 papers, Haiku, strict mode)

| Run | No lit. check | v2.6 | v2.6.1 |
|---|---|---|---|
| eccv-3d-2607.26889-flaw (planted test-set tuning, supplement §8.1) | 3 | 3, flaw **missed** | 3, flaw **caught and upheld** (DA-C1 quotes §8.1) |
| cvpr-3d-2607.02015 | 4 | 3 | 3 (single runs, unreported hyperparameters, colour claim without baselines; no recent-preprint weakness) |
| eccv-vlm-2609.16847 | 4 | 3 | 3 (DA-C1 upheld: prompt and training strategies selected on REGMB results that are also the headline numbers; REGMB has no validation split; grounded in §5.2 and App. C.2) |
| iclr-detseg-2604.14684 | 4 | 3 | **4** |
| eccv-generation-2609.28473 | 4 | 3 | **4** |

- The literature check no longer lowers clean papers by itself: 2 of 4 return to the no-search decision, and none of the remaining drops rests on a recent preprint or concurrent work.
- The protocol sweep found the buried supplement statement in the control, and a real, disclosed test-set selection in one clean paper (eccv-vlm). That second case follows criterion 3 as written; its measured effect is small (~1.5 points), so whether disclosed per-task selection should be MAJOR rather than CRITICAL is an open calibration question.
- Leaks: 0 of 240 kept results; the filter dropped the reviewed paper 4 times unread. 24/24 recommended references verified.
