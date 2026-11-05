# Literature-check evaluation (strict mode)

Runs complete: 11/11

## Leak check (primary)

- Kept results that are the reviewed paper (true title / arXiv ID): **0**
- Times the filter caught the reviewed paper and dropped it unread: 17 (in 10 runs)
- Runs with a ledger: 11/11

## Search activity

- Queries sent: 66 (mean 6.0 per run); refused by the guard: 1
- Results kept: 744; dropped: 338
- Recommended references verified with a link: 72/73 (78 verify calls)

## Decisions vs. the same paper without the literature check

| Run | Control | Without lit. check | With lit. check | DA-CRITICAL upheld | Queries | Kept | Self dropped | Refs verified |
|---|---|---|---|---|---|---|---|---|
| cvpr-3d-2607.02015-lit26 | no | 4 | 3 | 0 | 10 | 92 | 0 | 8/8 |
| eccv-vlm-2609.16847-lit26 | no | 4 | 3 | 0 | 8 | 135 | 2 | 8/9 |
| iclr-detseg-2604.14684-lit26 | no | 4 | 3 | 1 | 5 | 35 | 2 | 9/9 |
| eccv-generation-2609.28473-lit26 | no | 4 | 3 | 0 | 6 | 85 | 1 | 8/8 |
| cvpr-detseg-2604.24119-flaw-lit26 | yes | 3 | 3 | 1 | 5 | 84 | 1 | 5/5 |
| cvpr-lowlevel-2609.15120-flaw-lit26 | yes | 3 | 3 | 1 | 5 | 43 | 1 | 4/4 |
| eccv-3d-2607.26889-flaw-lit26 | yes | 3 | 3 | 0 | 5 | 53 | 2 | 5/5 |
| eccv-video-2608.07663-flaw-lit26 | yes | 3 | 3 | 1 | 6 | 39 | 2 | 5/5 |
| iclr-video-2604.18367-flaw-lit26 | yes | 3 | 3 | 1 | 5 | 51 | 2 | 6/6 |
| iclr-efficient-2601.20232-flaw-lit26 | yes | 3 | 3 | 1 | 5 | 29 | 2 | 5/5 |
| cvpr-detseg-2604.24119-plag-lit26 | no | 3 | 4 | 0 | 6 | 98 | 2 | 9/9 |

- Runs with a similarity check: 11/11; with a novelty delta table: 11/11
- Runs with any text-overlap flag: 1

**Planted plagiarism (cvpr-detseg-2604.24119-plag-lit26)**: similarity flagged the source: True; reported as an integrity concern: True; review uses the word 'plagiarism' (should be avoided): False; final 4

Controls still caught (upheld and ≤ 3): 5/6
