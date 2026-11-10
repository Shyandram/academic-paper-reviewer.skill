# ICLR 2026 calibration pilots

Pilots for the paperreview.ai-style evaluation (`evals/iclr_calibration.py`,
`.github/workflows/iclr-calibration.yml`). Per-paper numbers: `evals/iclr2026_pilot_scores.json` (pilots),
`evals/iclr2026_full_scores.json` (full evaluation, AI outputs only).
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

## Full evaluation: skill 2.10.1, 86 papers (Sonnet, high effort)

The balanced set of the protocol: 86 papers (45 train / 41 test; 23 accepted, 43 rejected,
17 withdrawn, 3 desk-rejected), single context, API. 66 papers were reviewed in run
42825160181; pilot 3's 20 runs are reused (2.10.1 has the 2.10 panel, scoring and decision;
only optional post-review parts changed). 86/86 runs finished. Cost $166.61 in total,
$1.94 per paper (median $1.91, range $1.29–2.88; $127.16 for the 66 new runs). Metrics: run 42840835940.

Spearman of the panel rating (reviewers' mean 1–6 Overall on the ICLR map, not fitted) with
the mean human rating [bootstrap 95% CI] / AUC for acceptance:

| Papers | n | Spearman | AUC |
|---|---|---|---|
| All | 86 | **+0.47** [+0.27, +0.64] | 0.64 |
| Pilot 3's 20 | 20 | +0.48 [+0.10, +0.74] | 0.67 |
| The 66 new papers | 66 | +0.48 [+0.25, +0.66] | 0.64 |
| Test split | 41 | +0.50 [+0.21, +0.72] | 0.67 |
| Test split, against one human (protocol) | 41 | +0.45 [+0.14, +0.69] | 0.67 |
| Without withdrawn papers | 69 | +0.40 [+0.17, +0.59] | 0.61 |
| Without the 11 papers the reviewer recognized | 75 | +0.48 [+0.28, +0.65] | 0.66 |

References on the same 86 papers: one human vs another Spearman +0.14, one human's AUC 0.64
(on the 41 test papers: −0.02 and 0.63). paperreview.ai (ICLR 2025): AI 0.42 / 0.75,
human 0.41 / 0.84.

| Predictor (86 papers) | NMAE ± std [CI] | NME ± std | Spearman | AUC |
|---|---|---|---|---|
| Panel rating | **0.084** ± 0.063 [0.071, 0.098] | **−0.003** ± 0.105 | +0.47 | 0.64 |
| Final rating (integer, ICLR scale) | 0.087 ± 0.064 [0.074, 0.102] | −0.018 ± 0.107 | +0.47 | 0.64 |
| Constant (median of these papers' mean ratings) | 0.089 ± 0.074 | — | — | — |
| One human vs mean human | 0.118 ± 0.087 | — | — | 0.64 |
| One human vs another human | 0.188 ± 0.157 | — | +0.14 | — |

Pipeline stages (Spearman, 86 papers; panel − stage [95% CI]): EIC-weighted rating 0.45
(+0.02 [−0.01, +0.06]), reviewers' pool position 0.48 (−0.01 [−0.06, +0.05]), EIC pool
position 0.45 (+0.02 [−0.03, +0.08]), panel without the DA 0.48 (−0.01 [−0.04, +0.02]).
No stage is better or worse than the panel rating.

The protocol's regression (7 EIC-weighted dimensions fitted on the 45 train papers, scored on
the 41 test papers against one human): Spearman +0.19 [−0.13, +0.48], AUC 0.67 [0.44, 0.87],
NMAE 0.084; without withdrawn papers +0.05. Three of the seven fitted weights are negative
(clarity, experimental validation, reproducibility): 45 papers do not fit seven correlated
dimensions, and the unfitted panel rating ranks the same test papers better (+0.45).

Rating spread: the final Overall is 3 (ICLR 4) for 67 of 86 papers, 2 for 10 and 4 for 9.
Mean panel rating (ICLR scale) by decision, AI / human: accepted 4.45 / 5.28, rejected
4.10 / 3.89, withdrawn 3.79 / 3.22, desk-rejected 3.87 / 4.56. The order is right, but the
accepted − rejected gap is 0.35 points against the humans' 1.39.

- **The pilot 3 signal holds.** The 66 new papers give the same Spearman as pilot 3's 20
  (0.48 and 0.48); it was not a lucky sample.
- **Ranking is above one-human agreement on the same papers** (0.47 vs 0.14) and at
  paperreview.ai's AI level (0.42, other year and papers). Acceptance AUC (0.64) equals one
  human's here but is below paperreview.ai's 0.75.
- **Not driven by recognized papers**: the reviewer said it knew 11 of the 86 (13%); without
  them Spearman is unchanged (0.48). Unlike pilot 3, they are not all rated high (EIC pool
  position 47–70).
- **Withdrawn papers carry part of the signal**: without them Spearman falls to 0.40.
- **Use the continuous panel rating**, not the regression over dimensions. The final integer
  rating ranks as well here (0.47) but puts 78% of papers on one value.
- **Compression is the main weakness**: good papers are under-rated (accepted papers
  0.8 points below the humans) and weak ones over-rated.
- **No score leak**: the reviewers' workspace held no human scores for the 66 new papers
  (`evals/iclr2026_pilot_scores.json` covers only the pilot papers); from commit cc5fffd the
  workflow also removes all evaluation data from the reviewer's workspace.

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

## Issue overlap and hit rate (reviewers vs human reviews)

Same 20 papers, pilot 3 (Sonnet high, skill 2.10, single context), compared with the ICLR 2026
human reviews of each paper (JerMa88/ICLR_Peer_Reviews_2026; 3–5 reviews, mean 4.05).
`evals/issue_overlap.py` takes the **weakness** sections of both panels (the Devil's
Advocate's issue list), and one Sonnet annotator per paper (`evals/issue_overlap_prompt.md`)
splits them into atomic points, groups the points into issues within each panel and matches
issues across panels. The annotator sees the panels under random names in random order,
without roles, and does not judge correctness. Main issues only (minor and cosmetic points
excluded). Numbers: `evals/iclr2026_issue_overlap.json`; 95% bootstrap CIs over papers.

| | Human | AI, 5 reviewers | AI, R1–R4 |
|---|---|---|---|
| Main issues per paper | 12.4 [10.8, 13.9] | 20.9 [19.0, 22.9] | |
| Share raised by one reviewer only | 0.77 [0.69, 0.83] | 0.49 [0.46, 0.53] | 0.73 [0.69, 0.77] |
| Pairwise Jaccard between reviewers | 0.10 [0.07, 0.14] | 0.16 [0.14, 0.18] | 0.10 [0.08, 0.12] |

| Hit rate | Value |
|---|---|
| Human issues raised by the AI panel | **0.45** [0.37, 0.54] |
| … raised by 2+ humans (consensus) | **0.78** [0.64, 0.90] |
| … raised by one human | 0.38 [0.28, 0.48] |
| … by the AI panel without the DA | 0.44 [0.37, 0.51] |
| AI issues also raised by a human | 0.26 [0.22, 0.29] |
| One human's issues raised by the *other* humans | 0.39 [0.31, 0.48] |
| One human's issues raised by 1 / 3 / 5 AI reviewers | 0.20 / 0.40 / 0.50 |

Coverage of the human issues by k AI reviewers (mean over subsets): 0.17, 0.29, 0.36, 0.41,
0.45 for k = 1–5.

| Role | Issues | Raised by no other role | Human issues hit | Hit by no other role |
|---|---|---|---|---|
| R1 Methodology | 10.1 | 0.23 | 0.19 | 0.01 |
| R2 Domain | 5.5 | 0.53 | 0.19 | 0.10 |
| R3 Perspective | 5.0 | 0.62 | 0.16 | 0.07 |
| R4 Generalist | 5.3 | 0.20 | 0.14 | 0.01 |
| Devil's Advocate | 9.2 | 0.09 | 0.20 | 0.02 |

Spearman of the mean Overall with the mean human rating, by reviewer subset (same pilot):
R1–R4 0.52, R1–R3 0.48, R2–R4 0.55, all five 0.48.

- **Overlap.** The five-reviewer panel looks more repetitive than a human panel, but at equal
  size (R1–R4, about the human panel size) the overlap is the same as the humans'. The
  repetition comes from the Devil's Advocate (91% of its issues raised by another role) and, to
  a lesser extent, R4 (80%) and R1 (77%, mostly shared with the DA).
- **Hit rate.** The panel raises 45% of the humans' main issues and 78% of those two or more
  humans agree on. Three AI reviewers anticipate a given human's issues as well as the other
  human reviewers do (0.40 vs 0.39); five do better (0.50).
- **Volume.** The AI panel raises about 1.7× as many main issues, and only a quarter of them
  were raised by a human. Unmatched issues are not necessarily wrong (humans miss things), but
  the EIC and authors need a short list.
- **Stability.** Four papers annotated twice by independent annotators: every metric above
  differs by at most 0.04.
- **Caveats.** n = 20; one LLM annotator per paper; humans saw the figures, the AI read the
  extracted text; agreement with humans is not correctness.

### What the panel misses, and why

`issue_overlap.py misses` lists each of the 247 human main issues with its status: **hit**
(matched by an AI main issue, 106), **related** (only a partial overlap with an AI issue, 115)
or **missed** (nothing close, 26). One Sonnet labeler per five papers (`evals/issue_miss_prompt.md`)
then gave each issue a topic, the evidence a reviewer needs to raise it, and, for the 141
non-hits, the likely reason, comparing it with that paper's AI issue summaries. Topic and
evidence were labeled before the labeler saw which issues were hit. The labeler did not see the
papers. Numbers: `evals/iclr2026_issue_misses.json` (pooled over issues; CIs by paper bootstrap).

| Topic | Issues | Hit rate [95% CI] |
|---|---|---|
| Missing experiments, ablations, datasets | 75 | 0.33 [0.23, 0.45] |
| Baselines | 33 | 0.58 [0.42, 0.75] |
| Scope, limitations, generalization | 33 | 0.39 [0.27, 0.54] |
| Novelty, related work | 25 | 0.56 [0.39, 0.76] |
| Method clarity | 23 | 0.30 [0.14, 0.50] |
| Unsupported claims | 19 | 0.37 [0.10, 0.67] |
| Theory | 19 | 0.58 [0.42, 0.75] |
| Efficiency | 10 | 0.90 [0.70, 1.00] |
| Presentation | 8 | 0.12 [0.00, 0.27] |

| Evidence needed | Issues | Hit rate |
|---|---|---|
| Paper text and tables | 175 | 0.41 |
| Outside knowledge (specific prior work, field norms) | 46 | 0.52 |
| Step-by-step derivation | 16 | 0.50 |
| Figures or qualitative results | 10 | 0.20 |

| Likely reason (141 non-hits) | Related | Missed |
|---|---|---|
| AI raised the same area only as a broad category | 69 | 0 |
| AI raised a related concern with a different diagnosis | 29 | 0 |
| Subjective request (more scope, another setting) | 6 | 13 |
| Fine technical or derivation detail | 3 | 7 |
| Needs figures or qualitative results | 2 | 3 |
| Needs a specific prior work | 3 | 1 |
| Unclear | 3 | 2 |

- **Mostly not blind spots but granularity.** 82% of the non-hits have a related AI issue. Half
  of all non-hits are cases where the panel said "more baselines" or "more ablations" and the
  human named which one; most of these human issues are specific (62 of 69).
- **Missing experiments** are the largest topic (30% of human issues) and among the least often
  hit (0.33): every reviewer can ask for a different experiment, and only a named one matches.
- **Not the expected causes.** Issues that need outside knowledge are hit *more* often (0.52)
  than text-only ones, so the literature check works; figures matter but are rare in weakness
  sections (10 issues, hit 0.20).
- **What is truly missed** (26) is mostly subjective scope requests (13) and fine technical
  detail (7). The labeler marked no human issue as likely wrong, but it could not check the
  paper.
- **Consensus.** Of the 52 issues raised by two or more humans, 37 were hit; 9 of the 15 others
  were raised only as a broad category.

### Raising the hit count: a Gap Scout pass

Most non-hits are issues the panel raised only as a category, so we tested one extra pass that
names items (`evals/gap_pass_prompt.md`, now `agents/gap_scout_agent.md`): one Sonnet agent per
paper read only the redacted paper and listed up to 30 concrete weaknesses reviewers would
likely raise (claims → missing evidence, named baselines, undefined elements, theory, scope,
typical requests). It never saw the reviews, scores or decisions. Then one annotator per paper
(`evals/gap_match_prompt.md`) matched each human main issue against the panel's main issues and
the Scout's items, mixed at random without sources (`issue_overlap.py match-prepare`,
`match-score`). Re-judged this way, the panel's hits agree with the original annotation on 88%
of human issues (0.47 vs 0.45). Numbers: `evals/iclr2026_gap_scout.json`.

| Source | Items per paper | Human main issues hit | Per-paper hit rate [95% CI] |
|---|---|---|---|
| Five-reviewer panel | 20.9 | 110 / 247 | 0.47 [0.38, 0.55] |
| Gap Scout, first 10 items | 10 | 70 | 0.30 [0.23, 0.39] |
| Gap Scout, first 20 items | 20 | 108 | 0.46 [0.39, 0.54] |
| Gap Scout, all items | 30 | 153 | **0.65** [0.59, 0.71] |
| Panel + Gap Scout | 50.9 | 175 | **0.73** [0.68, 0.79] |

- One concrete list of 20 items hits as many human issues as the whole five-reviewer panel
  with its 21 main issues; with 30 items it hits 1.4× as many. The hit count was still rising
  at 30 items.
- Of the 115 human issues the panel had only touched ("related"), the Scout matched 57; of
  the 26 the panel missed entirely, 14.
- By topic (panel → panel + Scout): missing experiments 0.35 → 0.76, baselines 0.55 → 0.82,
  scope 0.36 → 0.70, claims 0.37 → 0.63, method clarity 0.43 → 0.57; theory (0.63) and
  presentation (0.25) did not change.
- Caveats: the extra hits come partly from volume (51 items against about 12 human issues per
  paper); the Scout's items were not checked against the paper here (in 2.11 the Report
  Checker drops those the paper answers); same 20 papers and an LLM annotator.

**2.11 changes from this study**: the Devil's Advocate lists only issues that attack a step of
the core argument chain (no MINOR list); R4 keeps its vote (the ratings rank worse without it)
but lists weaknesses only from contribution clarity, venue fit and presentation; the Report
Checker adds the 3–5 key concerns; the report template asks each weakness to name the concrete
missing experiment, baseline or definition. A new unscored Gap Scout pass lists the concrete concerns reviewers are likely to raise
(Anticipated Reviewer Concerns checklist in the final report). To be measured with the same tool on the 2.11 runs.

**Later 2.11 changes from the role analysis.** With the Gap Scout in place, no human issue was
hit by the Devil's Advocate alone (unique hits: R1 0, R2 10, R3 3, R4 2, DA 0), and its rating
was the weakest panel signal (individual Overall vs human mean, Spearman: R1 0.27, R2 0.35,
R3 0.46, R4 0.41, DA 0.28). The Devil's Advocate is therefore no longer a panel reviewer: the
Report Checker runs the challenge after the report check, with no scores. R1 now writes its
main weaknesses from the claim-to-evidence map, naming the concrete item per claim, and R2
names the prior work behind every literature or baseline weakness. Measured in pilot 4 below.

### Pilot 4: skill 2.11 on the same 20 papers

Sonnet high, `check` pipeline over the API (four voting reviewers, Gap Scout, Report Checker
with the Devil's Advocate challenge, EIC). 20/20 runs finished; $138.61 in total, $6.93 per
paper (pilot 3: $1.97). Hits were annotated as in the Gap Scout study, with one fresh annotator
per paper on the same 247 human main issues (`issue_overlap.py run-prepare`, `run-score`).
Numbers: `evals/iclr2026_pilot4_hits.json`.

| Source (2.11) | Items per paper | Human main issues hit | Per-paper hit rate [95% CI] | Pilot 3 |
|---|---|---|---|---|
| Panel R1–R4 | 19.6 | 102 / 247 | 0.43 [0.35, 0.53] | 0.47 (five reviewers) |
| Devil's Advocate (in the checker) | 3.8 | 5 | 0.01 [0.01, 0.03] | — |
| Gap Scout, all items | 29.6 | 155 | 0.65 [0.58, 0.72] | 0.65 |
| Gap Scout, kept by the checker | 28.8 | 153 | 0.65 [0.57, 0.71] | — |
| Panel + Gap Scout | 49.2 | 178 | **0.74** [0.68, 0.80] | 0.73 |
| Everything | 53.0 | 180 | 0.75 [0.69, 0.81] | — |

- **No gain in hits.** The panel hits about what pilot 3's panel did on the same issues
  (0.43 vs 0.45 for pilot 3's panel under the original annotation); the named-item
  instructions for R1 and R2 did not raise the panel's hit rate. Unique hits (no other source):
  R1 2, R2 9, R3 4, R4 4, DA 2, Gap Scout 75.
- The checker dropped 0.85 Scout items per paper, losing 2 hits.
- The Devil's Advocate now attacks the argument chain rather than listing issues, and almost
  never matches a human issue; its role is the DA-CRITICAL ceiling (one raised and upheld).
- **Ratings ranked worse** (paired difference of the panel rating, pilot 4 − pilot 3:
  −0.15 [−0.48, 0.17]; the two pilots' panel ratings correlate at 0.78). Ratings were
  compressed: R1 gave 2 on 13 papers, R4 gave 3 on 17, and 10 papers have a panel rating of
  2.75. Individual reviewers (Spearman): R1 0.17, R2 0.12, R3 0.38, R4 0.26 (pilot 3: 0.27,
  0.35, 0.46, 0.41).

Ranking and error, same papers (`iclr_calibration.py pilot`; numbers:
`evals/iclr2026_pilot4_scores.json`):

| Predictor | Pilot 3 Spearman / AUC | Pilot 4 Spearman [95% CI] / AUC | Pilot 3 NMAE / NME | Pilot 4 NMAE / NME |
|---|---|---|---|---|
| Panel rating | **0.48** / **0.67** | 0.32 [−0.19, 0.74] / 0.55 | **0.079** / +0.004 | 0.083 / −0.028 |
| Final integer rating (ICLR scale) | 0.26 / 0.53 | 0.24 [−0.36, 0.70] / 0.47 | 0.090 / +0.010 | 0.102 / −0.050 |
| Constant (median) | — | — | 0.085 | 0.085 |

| Stage | Pilot 3 Spearman / AUC | Pilot 4 Spearman / AUC | Panel − stage, pilot 4 [95% CI] |
|---|---|---|---|
| Panel rating | 0.48 / 0.67 | 0.32 / 0.55 | — |
| Reviewers' pool position | 0.45 / 0.63 | 0.35 / 0.54 | −0.03 [−0.24, 0.19] |
| EIC-weighted rating | 0.42 / 0.63 | 0.36 / 0.57 | −0.04 [−0.20, 0.11] |
| EIC pool position | 0.30 / 0.55 | 0.35 / 0.54 | −0.03 [−0.24, 0.19] |
| Checker-weighted rating | — | 0.38 / 0.57 | −0.06 [−0.22, 0.10] |
| Checker's pool position | — | 0.39 / 0.59 | −0.07 [−0.35, 0.19] |
| **Checker's rating** | — | **0.51 / 0.67** | −0.19 [−0.73, 0.32] |
| Panel rating, voters + checker | — | 0.43 / 0.60 | −0.11 [−0.28, 0.02] |

- The panel rating barely beats the constant on NMAE (0.083 vs 0.085); the integer rating is
  worse than the constant and ranks at chance (AUC 0.47), and is slightly low (NME −0.05).
- Unlike pilot 3, the later stages rank slightly better than the panel, because the panel is
  weaker; no difference excludes 0.
- Decisions: 3 on 15 papers (leaning 2 on 7, leaning 4 on 6), 2 on 4, 4 on 1 (pilot 3: 3 on
  17). The EIC changed the starting decision on 1 paper (pilot 3: 0). 4 papers recognized
  (pilot 3: 3), no injection found.
- Reading: the hit count comes from the Gap Scout; the 2.11 panel changes cost money and some
  ranking signal without adding hits. The fresh-context checker's own estimate was the best
  single rating signal. n = 20; all intervals are wide.

**How good is the checker's own estimate?** Spearman with the human mean 0.51 [0.15, 0.77]
(the only rating whose interval excludes 0 in pilot 4), AUC 0.67, NMAE 0.081 (constant 0.085),
NME 0.00; on the 16 papers it did not recognize, 0.60 (panel 0.37). But its Overall takes three
values (3 on 14 papers, 4 on 4, 2 on 2), so the correlation rests on the 4 papers it rated 4
(3 accepted, 1 reject with human mean 4.0), and two accepted papers with human mean 4.4 and 6.0
got 3. Its continuous pool position ranks worse (0.39). It agrees little with the panel
(Spearman 0.38), which is why adding it as a fifth voice helps (0.43). Its advantage over the
panel is not established: difference 0.19 [−0.32, 0.70]. As a filter of the Gap Scout list it
dropped 17 of 592 items; 2 of them matched a human issue (12%, against 29% of the kept items),
so its drops are mostly right but too few to change the list. Its factual-error findings were
not verified against the papers in this pilot.

**Decision (2.10.1):** the panel, its instructions, the scoring and the decision rule go back to
2.10. The Gap Scout is taken out of the review: it runs only on request, after the review (or
on its own), in a context that has not seen it, and never changes it. The Report Checker is
removed. Its estimate (0.51) is no better than the 2.10 panel (0.48) within these error bars,
and it used only three Overall values; a planned test of it as a post-review analysis on the
pilot 3 reviews was cancelled, so its fact check was never measured.

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
- The final rating carries more signal than the plain mean of dimensions. On the full balanced
  set (86 papers) the protocol's regression over the 7 dimensions does worse than the unfitted
  panel rating (test split 0.19 vs 0.45); see "Full evaluation".
- Recognized papers all scored high (EIC 65–70) regardless of outcome; report them separately.
- 20 papers give wide intervals; the full 86-paper evaluation above is the result to cite.

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
