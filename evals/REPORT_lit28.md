# Literature-check evaluation (strict mode)

Runs complete: 2/2

## Leak check (primary)

- Kept results that are the reviewed paper (true title / arXiv ID): **0**
- Times the filter caught the reviewed paper and dropped it unread: 2 (in 1 runs)
- Runs with a ledger: 2/2

## Search activity

- Queries sent: 22 (mean 11.0 per run); refused by the guard: 1
- Results kept: 236; dropped: 101
- Recommended references verified with a link: 20/20 (20 verify calls)

## Decisions vs. the same paper without the literature check

| Run | Control | Without lit. check | With lit. check | DA-CRITICAL upheld | Queries | Kept | Self dropped | Refs verified |
|---|---|---|---|---|---|---|---|---|
| eccv-vlm-2609.16847-lit28 | no | 4 | 3 | 1 | 11 | 107 | 0 | 7/7 |
| eccv-generation-2609.28473-lit28 | no | 4 | 4 | 0 | 11 | 129 | 2 | 13/13 |

- Runs with a similarity check: 2/2; with a novelty delta table: 2/2
- Runs with any text-overlap flag: 0

## v2.7 search structure

| Run | Queries by purpose | Over budget | Scout calls | Claims with verdict | Verdicts | Missing prior baselines | Under-reported | Scout table | Field snapshot |
|---|---|---|---|---|---|---|---|---|---|
| eccv-vlm-2609.16847-lit28 | {'claim': 3, 'baseline': 3, 'expansion': 5} | 0 | 3 | 3 | {'C1': 'medium', 'C2': 'incremental', 'C3': 'medium'} | 6 | 0 | yes | yes |
| eccv-generation-2609.28473-lit28 | {'claim': 4, 'baseline': 3, 'expansion': 4} | 0 | 4 | 4 | {'C1': 'medium', 'C2': 'medium', 'C3': 'medium', 'C4': 'incremental'} | 0 | 0 | yes | yes |

## Notes (v2.8.1 reruns of the two v2.7 problem runs)

- **eccv-vlm:** DA-C1 is upheld again, now through the criterion-3 decision table. The selected Stage-III configuration's 79.9 (Table 7) equals the headline value in Tables 1 and 5, and no validation split is named, so the final score is 3. The run matches v2.6.1, and the v2.7 downgrade is fixed.
- **eccv-generation:** `review.md` is written, with the baseline scout table and field snapshot. The final score is 4, with no DA-CRITICAL issue, the same as v2.7.
