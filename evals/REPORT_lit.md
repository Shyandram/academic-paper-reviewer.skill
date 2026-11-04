# Literature-check evaluation (v2.5, strict mode)

Runs complete: 1/10

## Leak check (primary)

- Kept results that are the reviewed paper (true title / arXiv ID): **0**
- Times the filter caught the reviewed paper and dropped it unread: 2 (in 1 runs)
- Runs with a ledger: 1/1

## Search activity

- Queries sent: 7 (mean 7.0 per run); refused by the guard: 0
- Results kept: 38; dropped: 11
- Recommended references verified with a link: 9/9 (10 verify calls)

## Decisions vs. the same paper without the literature check

| Run | Control | Without lit. check | With lit. check | DA-CRITICAL upheld | Queries | Kept | Self dropped | Refs verified |
|---|---|---|---|---|---|---|---|---|
| cvpr-3d-2607.02015-lit | no | 4 | 3 | 0 | 7 | 38 | 2 | 9/9 |

- Runs with a similarity check: 0/1; with a novelty delta table: 0/1
- Runs with any text-overlap flag: 0
