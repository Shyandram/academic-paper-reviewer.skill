# ICLR 2026 calibration pilots

Pilots for the paperreview.ai-style evaluation (`evals/iclr_calibration.py`,
`.github/workflows/iclr-calibration.yml`). Per-paper numbers: `evals/iclr2026_pilot_scores.json`.
Review text and manuscripts are not committed.

## Setup

- Sample: ICLR 2026, seed 2025, 300 drawn, 295 with human scores (JerMa88 dataset).
- Paper text: arXiv v1 posted before the 2026-01-26 decision date, author block, emails, links,
  acknowledgments and line numbers removed. Reviewers see no human scores or decisions.
- Pilot set: 20 papers stratified by decision and human score: 5 accept, 10 reject, 4 withdrawn, 1 desk.

| Pilot | Skill | Model / effort | Text | Result |
|---|---|---|---|---|
| 1 | 2.9 | Haiku / default | mixed PDFs (camera-ready leak) | scores compressed, Spearman −0.12, AUC 0.47 |
| 2 | 2.10 | Haiku / default | normalized arXiv | Spearman −0.01, AUC 0.49 (mean of 6 dimensions) |
| 3 | 2.10 | Sonnet / high | normalized arXiv | see below |

Pilots 2 and 3 review the same 20 papers; 12 of them are also in pilot 1.

## Results (pilots 2 and 3, same 20 papers)

Each cell: Spearman with the mean human rating [bootstrap 95% CI] / AUC for acceptance.

| Model | Final rating (1–6) | EIC pool position | Mean of 6 dimensions | Cost |
|---|---|---|---|---|
| Haiku, default effort | +0.20 [-0.21, +0.58] / 0.56 | -0.06 [-0.55, +0.42] / 0.42 | -0.01 [-0.52, +0.49] / 0.49 | $17.18 |
| Sonnet, high effort | +0.48 [+0.09, +0.74] / 0.67 | +0.30 [-0.14, +0.69] / 0.55 | +0.22 [-0.27, +0.64] / 0.57 | $39.46 |

Human reference on the same papers: one reviewer vs another Spearman +0.12, one-reviewer AUC 0.58.
Larger references: our 2026 test split 0.25 / 0.75; paperreview.ai (ICLR 2025) AI 0.42 / 0.75, human 0.41 / 0.84.

Without the 3 papers Sonnet recognized (n = 17):

| Model | Final rating | EIC pool position | Mean of 6 dimensions | Cost |
|---|---|---|---|---|
| Haiku, default effort | +0.07 [-0.39, +0.49] / 0.50 | -0.25 [-0.71, +0.27] / 0.33 | -0.10 [-0.62, +0.44] / 0.44 | $14.22 |
| Sonnet, high effort | +0.46 [+0.09, +0.74] / 0.69 | +0.22 [-0.24, +0.66] / 0.53 | +0.10 [-0.41, +0.60] / 0.54 | $33.51 |

## Reading

- Haiku has no signal: all scores sit near the acceptance bar (EIC pool position 38–50) whatever the paper.
- Sonnet at high effort gives the first signal that is distinguishable from zero (final rating CI excludes 0),
  at about human-human agreement; AUC is still below paperreview.ai's 0.75.
- The final rating carries more signal than the plain mean of dimensions; the protocol's linear
  regression over the 7 dimensions needs the full balanced set (86 papers, 45 train / 41 test).
- Recognized papers all scored high (EIC 65–70) regardless of outcome; report them separately.
- 20 papers give wide intervals; these are pilot numbers, not the evaluation result.

## Per paper (sorted by mean human rating)

| Paper | Decision | Human mean | Haiku rating / EIC | Sonnet rating / EIC | Sonnet recognized |
|---|---|---|---|---|---|
| AIKURJjxXT | Withdrawn | 2.50 | 3.2 / 40 | 2.8 / 40 |  |
| KtocialdxS | Reject | 2.67 | 3.4 / 48 | 3.0 / 45 |  |
| 8xcmfwomnI | Reject | 3.00 | 3.0 / 40 | 3.0 / 42 |  |
| g4HpTtgsn2 | Withdrawn | 3.00 | 3.2 / 46 | 2.6 / 38 |  |
| E5mL07Fbq8 | Reject | 3.33 | 3.0 / 38 | 2.6 / 42 |  |
| Z6z4AnXGhw | Reject | 3.50 | 3.4 / 50 | 3.2 / 50 |  |
| gUw8n109ki | Withdrawn | 3.50 | 3.2 / 50 | 2.6 / 40 |  |
| 0xObmDmsKY | Reject | 4.00 | 3.2 / 46 | 3.0 / 45 |  |
| BxeJLOrKDF | Withdrawn | 4.00 | 3.2 / 45 | 3.2 / 45 |  |
| Jw7khYzYzl | Reject | 4.00 | 3.6 / 45 | 4.0 / 70 | yes |
| 9jcB40wjk3 | Accept (Poster) | 4.40 | 2.8 / 40 | 2.8 / 38 |  |
| be4ey66fhk | Reject | 4.40 | 3.2 / 45 | 3.4 / 52 |  |
| 9R2iUHhVfr | Reject | 4.50 | 3.4 / 50 | 3.6 / 65 | yes |
| PJdMrK79Mo | Accept (Poster) | 4.50 | 3.6 / 48 | 3.4 / 50 |  |
| qfW4IrUuig | Reject | 4.50 | 3.0 / 40 | 2.8 / 40 |  |
| Lvkbe0CgmZ | Reject | 5.00 | 3.4 / 40 | 3.2 / 45 |  |
| tlYSbw5GXY | Accept (Poster) | 5.20 | 3.2 / 38 | 3.4 / 55 |  |
| euMVC1DO4k | Accept (Poster) | 6.00 | 3.6 / 50 | 3.8 / 68 | yes |
| kwro5432AI | Desk rejected | 6.00 | 3.2 / 45 | 3.0 / 42 |  |
| rubeJmT1XM | Accept (Poster) | 6.00 | 3.2 / 40 | 3.0 / 40 |  |
