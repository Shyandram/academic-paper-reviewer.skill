# Literature-check evaluation (strict mode)

Runs complete: 5/5

## Leak check (primary)

- Kept results that are the reviewed paper (true title / arXiv ID): **0**
- Times the filter caught the reviewed paper and dropped it unread: 10 (in 5 runs)
- Runs with a ledger: 5/5

## Search activity

- Queries sent: 52 (mean 10.4 per run); refused by the guard: 1
- Results kept: 362; dropped: 170
- Recommended references verified with a link: 28/28 (30 verify calls)

## Decisions vs. the same paper without the literature check

| Run | Control | Without lit. check | With lit. check | DA-CRITICAL upheld | Queries | Kept | Self dropped | Refs verified |
|---|---|---|---|---|---|---|---|---|
| cvpr-3d-2607.02015-lit27 | no | 4 | 3 | 0 | 9 | 17 | 3 | 3/3 |
| eccv-vlm-2609.16847-lit27 | no | 4 | 4 | 0 | 12 | 81 | 2 | 5/5 |
| iclr-detseg-2604.14684-lit27 | no | 4 | 4 | 0 | 10 | 56 | 1 | 6/6 |
| eccv-generation-2609.28473-lit27 | no | 4 | 4 | 0 | 12 | 116 | 2 | 5/5 |
| eccv-3d-2607.26889-flaw-lit27 | yes | 3 | 3 | 1 | 9 | 92 | 2 | 9/9 |

- Runs with a similarity check: 5/5; with a novelty delta table: 4/5
- Runs with any text-overlap flag: 0

## v2.7 search structure

| Run | Queries by purpose | Over budget | Scout calls | Claims with verdict | Verdicts | Missing prior baselines | Under-reported | Scout table | Field snapshot |
|---|---|---|---|---|---|---|---|---|---|
| cvpr-3d-2607.02015-lit27 | {'claim': 4, 'expansion': 5} | 0 | 0 | 4 | {'C1': 'medium', 'C2': 'medium', 'C3': 'incremental', 'C4': 'incremental'} | 1 | 0 | yes | yes |
| eccv-vlm-2609.16847-lit27 | {'claim': 5, 'baseline': 3, 'expansion': 4} | 0 | 14 | 4 | {'C1': 'medium', 'C2': 'incremental', 'C3': 'medium', 'C4': 'incremental'} | 2 | 0 | yes | yes |
| iclr-detseg-2604.14684-lit27 | {'claim': 4, 'baseline': 2, 'expansion': 4} | 0 | 2 | 4 | {'C1': 'medium', 'C2': 'incremental', 'C3': 'medium', 'C4': 'medium'} | 2 | 0 | yes | yes |
| eccv-generation-2609.28473-lit27 | {'claim': 4, 'baseline': 3, 'expansion': 5} | 1 | 6 | 3 | {'C1': 'medium', 'C2': 'incremental', 'C3': 'medium'} | 0 | 0 | no | no |
| eccv-3d-2607.26889-flaw-lit27 | {'claim': 4, 'baseline': 2, 'expansion': 3} | 0 | 3 | 3 | {'C1': 'medium', 'C2': 'medium', 'C3': 'medium'} | 4 | 0 | yes | yes |

Controls still caught (upheld and ≤ 3): 1/1

## Notes

- **eccv-generation-lit27:** the agent declined to write `review.md` and returned the review in its reply. The audit therefore shows no scout table or field snapshot for it; its search files and scores are complete.
- **eccv-vlm-lit27:** DA-C1 (per-task selection on a benchmark without a validation split, disclosed) was upheld in v2.6.1 and downgraded to MAJOR here. Same paper, same skill rules, so this is run-to-run variance in applying the CRITICAL criteria.
- **cvpr-3d:** 4 without the literature check, 3 with it (two incremental claims plus a missing prior baseline). v2.6.1 gave 4.
- **Panel diversity** (TF-IDF, 1 − mean pairwise cosine between the five reports): 0.614 mean over v2.7 + v2.6.1. Rerun diversity on the same paper is 0.15–0.22, so reruns share much of their content but are not copies.
