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

## Error on the ICLR scale (NMAE / NME)

CSPaper-style errors against the mean human rating on the ICLR 2026 scale (0–10):
NMAE = mean |human − AI| / 10 (lower is better), NME = signed mean (0 is unbiased), ± std across
papers, 95% bootstrap CI. "Panel rating" maps the reviewers' mean 1–6 Overall with the skill's
ICLR map (2·(x − 1)); "final rating" is the skill's integer rating on the ICLR scale.
Computed with `python3 evals/iclr_calibration.py pilot sample.jsonl features.jsonl`.

| Predictor | NMAE ± std [CI] | NME ± std | Spearman | AUC |
|---|---|---|---|---|
| Haiku, panel rating | 0.093 ± 0.057 [0.068, 0.118] | +0.030 ± 0.105 | +0.21 | 0.56 |
| Haiku, final rating | 0.085 ± 0.063 [0.058, 0.115] | −0.020 ± 0.104 | n/a (constant) | 0.50 |
| Sonnet high, panel rating | **0.079 ± 0.061** [0.054, 0.106] | **+0.004** ± 0.100 | **+0.48** | **0.67** |
| Sonnet high, final rating | 0.090 ± 0.064 [0.061, 0.119] | +0.010 ± 0.110 | +0.26 | 0.53 |
| Constant (median of these papers' mean ratings) | 0.085 ± 0.060 | — | — | — |
| One human vs another human | 0.180 ± 0.125 | — | +0.12 | — |
| One human vs mean human | 0.102 ± 0.065 | — | — | 0.58 (one human) |

- NMAE rewards staying near the middle: an oracle constant scores 0.085, so NMAE alone does not
  show skill. Haiku's final rating is the same integer for every paper and still "beats" humans.
  Read NMAE together with Spearman/AUC; only Sonnet's panel rating beats the constant and ranks papers.
- NME ≈ 0: after the 2.10 calibration the ratings are no longer biased low or high on this pool.
- The integer final rating loses ranking signal against the continuous panel mean (Spearman 0.26 vs 0.48).
- Reference only (not comparable: unknown N and paper overlap): CSPaper reports NMAE 0.128,
  NME −0.015, SRC 0.658 for Claude Sonnet 5.5 on ICLR main.

## Where the signal is lost (reviewers → EIC)

Sonnet high, 20 papers. Spearman with the mean human rating at each stage, and the paired
bootstrap difference from the reviewers' mean rating (> 0: the reviewers' mean ranks better).
Computed by `iclr_calibration.py pilot` (`stages`).

| Stage | Spearman | AUC | Reviewers' mean − stage [95% CI] |
|---|---|---|---|
| Reviewers' mean Overall (panel rating) | 0.48 | 0.67 | — |
| Reviewers' mean pool position | 0.45 | 0.63 | +0.03 [−0.11, +0.18] |
| EIC-weighted rating | 0.42 | 0.63 | +0.06 [−0.03, +0.17] |
| EIC pool position | 0.30 | 0.55 | **+0.18 [+0.01, +0.40]** |
| Final integer decision | 0.26 | 0.53 | +0.22 [−0.08, +0.51] |

- The EIC never changed the starting decision (0/20), and the DA cap never pushed a decision
  below the reviewers' rating. The loss is not from overrides.
- **Integer decision**: 17/20 papers get 3, so the final rating barely separates papers.
- **EIC pool position**: the EIC's own estimate is weaker than the mean of the five
  reviewers' estimates. This is the only difference whose CI excludes 0.
- **Quality weighting**: a small loss (the EIC-weighted rating moves 0.08 from the plain mean
  on average). With Haiku the loss is larger (0.20 → 0.04, CI [+0.01, +0.34]).
- Each reviewer's Overall uses only 2–3 values across the 20 papers. The continuous pool
  positions carry comparable signal.

**Decision**: no skill change yet; confirm on the full balanced evaluation first. Candidate
changes:
1. use the continuous panel rating as the primary score;
2. use the reviewers' mean pool position instead of the EIC's;
3. report a lean with the integer decision (e.g. "3, leaning 4").

## Split pipeline trial (3 papers)

Sonnet high, `evals/split/` (one fresh context per phase), run as in-session subagents
(no API billing, no shared prompt cache). Same three papers as the single-context Sonnet pilot.

| Paper | Human mean | Single: Overall / rating / final | Split: Overall / rating / final |
|---|---|---|---|
| iclr26-g4HpTtgsn2 | 3.0 (Withdrawn) | 2,3,3,3,2 / 2.6 / 3 | 2,2,2,2,2 / 2.0 / 2 |
| iclr26-0xObmDmsKY | 4.0 (Reject) | 3,3,4,3,2 / 3.0 / 3 | 3,3,3,3,3 / 3.0 / 3 |
| iclr26-tlYSbw5GXY | 5.2 (Accept) | 3,3,4,4,3 / 3.4 / 3 | 3,3,3,3,3 / 3.0 / 3 |

- **No increase in spread.** The SD of the reviewers' Overall is 0 on every paper (single:
  0.49–0.63), and the SD of pool position falls from 6.5–10.1 to 1.0–4.8. The one-point R3
  (Perspective) optimism in the single context disappears.
- **Ranking**: the single context orders the three papers as the humans do; the split ties
  the Reject and the Accept paper. No DA-CRITICAL was raised; the EIC never left the start.
- **Cost**: $3.5–4.7 per paper (API-equivalent estimate from token counts) vs $1.7–1.9 for
  the single context. Cache writes are 0.73–0.87M tokens vs about 0.22M. Critical path
  10–11 min vs 9–10 min.
- **Independent check**: the Phase 1.5/1.6 check in a fresh context caught factual errors in
  the reports (miscounts, a metric value misquoted by three reviewers, an unverified
  attribution), and the EIC down-weighted R2 on all three papers.
- **Caveats**: n = 3. The reviewers still shared the phase-0 card and paper memory, so this
  tests separate reports, not separate readings of the paper. Read-deny rules were
  instructions only in subagent mode.

**Decision**: the split is not adopted. Evaluation runs continue with skill 2.10 (single
context). The independent check (a fresh-context Phase 1.5/1.6 after the reviewers) is planned
for the next skill version, to be evaluated against 2.10.

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
