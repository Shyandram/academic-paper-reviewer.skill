# ICLR 2026 calibration pilots

Pilots for the paperreview.ai-style evaluation (`evals/iclr_calibration.py`,
`.github/workflows/iclr-calibration.yml`). Per-paper numbers: `evals/iclr2026_pilot_scores.json` (pilots),
`evals/iclr2026_full_scores.json` (full evaluation, AI outputs only), `evals/iclr2026_issue_overlap_full.json`
(issue overlap on the 86 papers), `evals/iclr2026_codex_pilot3.json` (GPT-6.1 Terra vs Sonnet, 20 papers),
`evals/iclr2026_codex_sol_pilot3.json` (GPT-6.1 Sol vs Sonnet and Terra, same 20 papers),
`evals/iclr2026_issue_overlap_gpt.json` (issue overlap of the three models, same 20 papers),
`evals/iclr2026_sol_diagnosis.json` (why Sol does not rank them; `evals/sol_diagnosis.py`).
`evals/iclr2026_terra213_validation_r*.json` (skill 2.13 validation rounds, 3 papers each; `evals/validation_compare.py`).
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
(on the 41 test papers: −0.02 and 0.63).

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
- **Ranking is above one-human agreement on the same papers** (0.47 vs 0.14), roughly the level
  paperreview.ai reports for its AI reviewer (0.42, other year and papers). Acceptance AUC (0.64)
  equals one human's here.
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
Larger reference: human vs human on our 2026 test split 0.25 / 0.75.

Without the 3 papers Sonnet recognized (n = 17):

| Model | Final rating | EIC pool position | Mean of 6 dimensions | Cost |
|---|---|---|---|---|
| Haiku, default effort | +0.07 [-0.39, +0.49] / 0.50 | -0.25 [-0.71, +0.27] / 0.33 | -0.10 [-0.62, +0.44] / 0.44 | $14.22 |
| Sonnet, high effort | +0.46 [+0.09, +0.74] / 0.69 | +0.22 [-0.24, +0.66] / 0.53 | +0.10 [-0.41, +0.60] / 0.54 | $33.51 |

## Another model: GPT-6.1 Terra (high) via Codex, pilot 3's 20 papers

Run 42834172940, collected by run 42851251502 (metrics only; numbers in `evals/iclr2026_codex_pilot3.json`). Codex `exec` with
`model_reasoning_effort=high`, 2 papers in parallel, the same prompt and blinded text as the
Claude runs; skill 2.10.1 (the 2.10 panel without the Report Checker; Sonnet's pilot 3 ran
2.10). All 20 reviews finished; none failed. Spearman with the mean human rating [bootstrap
95% CI] / acceptance AUC; NMAE / NME on the ICLR scale.

| | Sonnet, high (pilot 3) | GPT-6.1 Terra, high |
|---|---|---|
| Panel rating (1–6) | **+0.48** [+0.12, +0.73] / 0.67 | -0.01 [-0.43, +0.43] / 0.40 |
| Reviewers' pool position | +0.45 [+0.03, +0.77] / 0.63 | +0.05 [-0.35, +0.51] / 0.45 |
| EIC pool position | +0.30 [-0.12, +0.68] / 0.55 | +0.10 [-0.34, +0.57] / 0.49 |
| ICLR rating | +0.26 [-0.10, +0.59] / 0.53 | +0.01 [-0.39, +0.44] / 0.41 |
| NMAE / NME, ICLR rating | 0.090 / +0.010 | 0.133 / -0.070 |
| ICLR ratings given (2 / 4 / 6) | 0 / 17 / 3 | 6 / 13 / 1 |
| SD of panel rating; of EIC pool | 0.38; 9.6 | 0.45; 11.3 |
| Papers recognized | 3 | 0 |
| Cost per paper | $1.97 (billed) | $4.55 (estimate from session-log tokens) |
| Wall time per paper | – | 9.2 min (6.2–14.4) |

Constant median: NMAE 0.085. Human references on the same papers as above.

- **No ranking signal.** GPT-6.1 Terra's panel rating does not track the human mean (Spearman
  -0.01, AUC 0.40); no stage helps (reviewers' pool +0.05, EIC pool +0.10).
- **It agrees with Sonnet more than with the humans.** Spearman between the two models: panel
  rating 0.65, EIC pool 0.67; same ICLR rating on 12 of 20 papers; mean absolute gap in the
  panel rating 0.36. The disagreement sits on the papers the humans liked: it rates all five
  accepted papers lower than Sonnet (by 0.2–0.8 on the 1–6 scale), and the accepted paper with
  the highest human mean (6.0) shares its lowest rating, 2.2.
- **Harsher and more spread out.** Six papers get ICLR 2 (Sonnet: none), so the scores are less
  compressed than Sonnet's (78% at ICLR 4 on 86 papers) but land on the wrong papers; NME -0.07.
- **Cost.** About 2.3× Sonnet's per-paper cost at list prices; the first attempt at 10 papers in
  parallel hit the organization's token-per-minute limit, so this run used 2.
- With 20 papers the interval is wide; the result says this model, prompted this way, gives no
  usable ranking here, not that it cannot.

### GPT-6.1 Sol (high), same 20 papers

Run 42857826982, same setup as the Terra run (Codex `exec`, `model_reasoning_effort=high`, 2 in
parallel, skill 2.10.1). All 20 reviews finished; none failed. Numbers in
`evals/iclr2026_codex_sol_pilot3.json`.

| | Sonnet, high | GPT-6.1 Terra, high | GPT-6.1 Sol, high |
|---|---|---|---|
| Panel rating (1–6) | **+0.48** [+0.12, +0.73] / 0.67 | -0.01 [-0.43, +0.43] / 0.40 | +0.02 [-0.38, +0.45] / 0.47 |
| Reviewers' pool position | +0.45 [+0.03, +0.77] / 0.63 | +0.05 [-0.35, +0.51] / 0.45 | -0.07 [-0.50, +0.44] / 0.45 |
| EIC pool position | +0.30 [-0.12, +0.68] / 0.55 | +0.10 [-0.34, +0.57] / 0.49 | -0.00 [-0.43, +0.45] / 0.47 |
| ICLR rating | +0.26 [-0.10, +0.59] / 0.53 | +0.01 [-0.39, +0.44] / 0.41 | +0.06 [-0.27, +0.42] / 0.39 |
| NMAE / NME, ICLR rating | 0.090 / +0.010 | 0.133 / -0.070 | 0.126 / -0.020 |
| ICLR ratings given (2 / 4 / 6) | 0 / 17 / 3 | 6 / 13 / 1 | 3 / 14 / 3 |
| SD of panel rating; of EIC pool | 0.38; 9.6 | 0.45; 11.3 | 0.34; 8.8 |
| Papers recognized | 3 | 0 | 1 |
| Cost per paper | $1.97 (billed) | $4.55 (estimate) | $1.39 (estimate) |
| Wall time per paper | – | 9.2 min (6.2–14.4) | 14.3 min (11.8–17.6) |

- **No ranking signal from Sol either.** Panel rating Spearman +0.02, AUC 0.47; no stage helps.
  Its ICLR ratings are not biased overall (NME -0.02) but land on the wrong papers: NMAE 0.126
  against 0.085 for a constant guess.
- **The two GPT models agree with each other, and with Sonnet, more than with the humans.**
  Panel rating Spearman: Sol–Terra 0.71, Sol–Sonnet 0.60, Terra–Sonnet 0.65; EIC pool: Sol–Terra
  0.82, Sol–Sonnet 0.74. Sol gives the same ICLR rating as Sonnet on 15 of 20 papers.
- **Same failure pattern as Terra.** The three papers with the highest human mean (6.0) get 3.4,
  2.8 and 2.8 from Sol, while the three with the lowest (2.5–3.0) each get 3.2. Sonnet's edge
  comes from a few papers at each end, so with 20 papers the gap is suggestive, not established:
  the intervals overlap. A paired bootstrap of the difference is tighter; see
  [Why Sol does not rank the papers](#why-sol-does-not-rank-the-papers).
- **Cost is not comparable between the two GPT rows.** The Sol estimate prices cached input at
  the list rate ($0.10 per 1M); the Terra estimate priced cached input the same as fresh input,
  so it overstates Terra's cost. Sol's list prices are $2 / $10 per 1M input / output.

### Beyond ranking: concerns raised by the three models

The same issue-overlap study as for Sonnet (`evals/issue_overlap.py`, one Sonnet annotator per
paper, main issues only), run on the GPT reviews of the same 20 papers. Numbers in
`evals/iclr2026_issue_overlap_gpt.json`; mean per paper [bootstrap 95% CI].

| | Sonnet, high | GPT-6.1 Sol, high | GPT-6.1 Terra, high |
|---|---|---|---|
| Human main issues raised by the panel (hit rate) | **0.45** [0.37, 0.54] | 0.21 [0.17, 0.25] | 0.27 [0.21, 0.34] |
| of those raised by 2+ humans | **0.78** [0.64, 0.90] | 0.27 [0.16, 0.38] | 0.50 [0.35, 0.66] |
| of those raised by one human | **0.38** | 0.18 | 0.20 |
| AI issues also raised by a human (precision) | 0.26 [0.22, 0.29] | 0.23 [0.19, 0.28] | **0.28** [0.23, 0.34] |
| AI main issues per paper | 20.9 | 10.8 | 10.9 |
| Pairwise Jaccard between the five AI reports | 0.16 | 0.16 | 0.19 |
| One human's issues raised by the other humans | 0.39 | 0.40 | 0.41 |

What the GPT models do well:

- **Same precision at half the length.** They raise about 11 main issues per paper against
  Sonnet's 21, and a similar share of them is something a human also raised (Terra 0.28, Sol
  0.23, Sonnet 0.26). An author reads half as much for the same density of human-matched points.
- **Sol is cheap and unbiased.** About $1.39 per paper against $1.97, NME -0.02.
- **More of the rating scale.** Sol gives 3 / 14 / 3 papers ICLR 2 / 4 / 6 and Terra 6 / 13 / 1,
  against Sonnet's 0 / 17 / 3.
- **Fewer recognized papers** (Terra 0, Sol 1, Sonnet 3), and Terra is the fastest (9 min per
  paper against Sol's 14).

Where they fall short: they raise half as many of the humans' issues (0.21 and 0.27 against
0.45), and the gap is largest on the issues two or more humans agree on (0.27 and 0.50 against
0.78). Together with the flat ranking, the extra spread in their scores does not land on the
right papers.

Caveat: the count uses each report's Weaknesses section (and the DA's issue list) only. Sol's
reviews are as long as Sonnet's overall (median 12.0k against 10.9k words) but its Weaknesses
sections are about half as long, because it puts more findings in separate audit sections
(claim-to-evidence, protocol sweep, error log), which this study leaves out for every model.

### Why Sol does not rank the papers

Sol was expected to land near Sonnet: it reads the whole paper, searches more, and writes
reviews of the same length. It does not. Numbers in `evals/iclr2026_sol_diagnosis.json`
(`evals/sol_diagnosis.py`, from the per-paper results; numbers and paper IDs only).

**The gap is real but its size is uncertain.** Paired bootstrap (5000 resamples of the 20
papers) of Sonnet's minus Sol's panel-rating Spearman: 0.46 [0.08, 0.81], P(difference ≤ 0) =
0.01. Sol is not noisy either: its reviewers' pool correlates 0.81 with Terra's and 0.61 with
Sonnet's, so it ranks by a consistent standard, just not the humans'.

**It does not separate the papers the humans liked from the rest.** Mean reviewers' pool
position on the humans' top 10 against bottom 10:

| | Sonnet | Sol | Terra |
|---|---|---|---|
| Reviewers' pool, top 10 / bottom 10 | 51.4 / 46.6 (+4.8) | 55.1 / 55.3 (−0.2) | 50.2 / 52.3 (−2.1) |
| Panel rating, top 10 / bottom 10 | 3.24 / 3.00 | 3.08 / 3.12 | 2.88 / 3.00 |

**1. Its scores follow rigor; the humans' follow novelty and significance.** Spearman of each
dimension with the model's own reviewers' pool, and with the human mean:

| Dimension | Sonnet: own pool / human | Sol: own pool / human | Terra: own pool / human |
|---|---|---|---|
| Technical rigor | 0.84 / +0.23 | **0.94** / +0.04 | 0.91 / −0.11 |
| Novelty | **0.92** / **+0.56** | 0.76 / +0.19 | 0.61 / +0.32 |
| Significance | 0.82 / +0.47 | 0.78 / +0.31 | 0.91 / +0.14 |
| Experimental validation | 0.67 / +0.24 | 0.88 / −0.02 | 0.94 / +0.05 |
| Clarity | 0.48 / +0.04 | 0.81 / −0.13 | 0.74 / −0.01 |

Sonnet's pool is driven most by novelty, the dimension that tracks the humans best. Sol's is
driven by rigor, experimental validation and clarity, which do not track the humans at all here.

**2. Lenient on weak papers whose problem is novelty.** On the humans' bottom papers Sol's
pool sits 12–16 points above Sonnet's (reviewers' pool, Sonnet / Sol): AIKURJjxXT 38.0 / 53.0,
g4HpTtgsn2 36.6 / 52.2, gUw8n109ki 40.4 / 53.2, KtocialdxS 44.8 / 56.4. The human reviews of
these papers lead with lack of novelty and name the prior work. Sol raises novelty only as a
question to clarify, without a named paper: none of its top concerns on any of the 20 papers
cites a prior work (author–year or bracket pattern), against 6 of 20 papers for Sonnet (Terra:
0 of 20). Its search effort is not the cause: median search-ledger entries per paper 190.5 for
Sol and 181 for Terra against 129 for Sonnet, kept results 86.5 and 92.5 against 51.5. The
searches return many keyword hits but, judging by the reviews, not the specific overlapping
paper, so the evidence rules leave the doubt unproven and lightly weighted.

**3. Harsh on theory papers with verifiable proof defects.** Lvkbe0CgmZ (human mean 5.0,
human rank 5): Sonnet ranks it 7th (pool 52.2, rigor 52.4, ICLR 4), Sol 19th (pool 44.2, rigor
38.5, ICLR 2) after logging a series of proof errors as verified. Sonnet flagged the same main
theorem defect and still gave ICLR 4; the human reviewers focused on the synthesis and the
gap to the exact dynamics, not on fatal errors. rubeJmT1XM (accepted, human mean 6.0, also
theoretical) is Sol's last of 20 (Sonnet 14th). Sol also gives ICLR 2 to 9jcB40wjk3 (accepted,
human mean 4.4; Sol rigor 42.9, Sonnet ICLR 4). A verified error weighs fully in
Sol's score; an unproven novelty doubt hardly at all.

**Hit rate by kind of human issue** (keyword categories on the issue summaries; crude). The
annotator extracts the human issues afresh for each model's study, so the counts differ by
column:

| Human main issues about… | Sonnet | Sol | Terra |
|---|---|---|---|
| Novelty / prior work | **0.70** (14/20) | 0.38 (10/26) | 0.44 (11/25) |
| Theory / proofs | 0.42 (5/12) | 0.19 (3/16) | 0.20 (4/20) |
| Experiments / baselines | **0.49** (34/70) | 0.18 (15/84) | 0.23 (17/73) |
| Clarity | 0.30 (11/37) | 0.12 (5/41) | 0.14 (5/35) |

**4. Less reasoning per paper.** Medians per paper:

| | Sonnet | Sol | Terra |
|---|---|---|---|
| Output tokens | 80.5k | 43.6k | 25.3k |
| Reasoning tokens | 30.2k | 9.3k | 4.6k |
| Wall time | 9.6 min | 14.0 min | 8.5 min |

Sol runs longer than Sonnet but reasons about a third as much; the time goes to tool calls and
searches. Deciding which prior paper a submission overlaps with, and whether a proof defect is
fatal, are the judgements that need it.

**Ruled out.** Reading (Sol reads the whole paper); review length (median 12.0k words against
Sonnet's 10.9k); search volume (above); reviewer independence (Sonnet's pilot also ran its
reviewers in sequence without subagents, and the within-paper spread of pool positions is
similar, SD 9.3 against 8.7).

**Caveats.** 20 papers. The issue categories and the citation pattern are keyword matches.
Agreeing with the human reviewers is not the same as being right: Sol's proof findings may be
correct and missed by the humans. The result says Sol, prompted this way at `high` effort,
weighs evidence differently from ICLR reviewers. Candidate fixes, not yet tested: require a
named closest prior work (or an explicit "none found") behind every novelty concern; grade a
verified error as fatal or repairable before it moves the score; rerun Sol at a higher reasoning
effort. Skill 2.13 implements the first two; its validation follows.

### Skill 2.13 validation (GPT-6.1 Terra, `high`, 3 papers per round)

This stage runs at most 3 papers per experiment, with a per-paper API cap enforced by
`evals/codex_budget_guard.py`. The three papers are pilot 3's KtocialdxS (human mean 2.67; Terra 2.10.1
lenient), Lvkbe0CgmZ (5.0; harsh on proof errors) and euMVC1DO4k (6.0; control). Three papers say whether
the new instructions are followed and which way the scores move, not whether ranking improves.

**Round 1** (skill 2.13 as first committed; `evals/iclr2026_terra213_validation_r1.json`):

| Paper | Human mean | Reviewer pool, 2.10.1 → 2.13 | EIC pool, 2.10.1 → 2.13 | Central-claim verdicts (2.13 profile) | paper_novelty |
|-------|-----------:|------------------------------|-------------------------|----------------------------------------|--------------:|
| euMVC1DO4k | 6.0 | 60.6 → 56.4 | 59 → 55 | high, incremental, medium | 0.59 |
| Lvkbe0CgmZ | 5.0 | 32.6 → 40.6 | 25 → 36 | medium, medium, medium | 0.50 |
| KtocialdxS | 2.67 | 57.4 → 56.2 | 55 → 55 | incremental, incremental, medium | 0.38 |

- The new instructions were followed: every prior match carried shared facets and a delta, the reports
  wrote both cases before the pool position, the errors carried repair tests, and novelty concerns
  reached the top concerns (KtocialdxS, euMVC1DO4k).
- The theory paper rose by 11 EIC points, as the repair test intends. The lenient case did not move.
- The claim-level profile ordered the three papers as the humans did (paper_novelty 0.59 > 0.50 > 0.38),
  but the pool positions did not use it: the lowest- and highest-rated papers both got an EIC pool of 55,
  and each report's deciding evidence was a routine evidence gap (no matched-quality or matched-cost
  comparison), which accepted papers often share.
- Cost at Terra's listed prices ($1 / $0.05 cached / $5 per 1M tokens): $0.39–0.51 per paper, against
  $0.35–0.44 for the same papers under 2.10.1. Earlier estimates in this report priced cached input as
  fresh and overstate Terra's cost about ninefold.
- Not fixed: the evaluation prompt still forbids `integrity_scan.py`, which the skill requires (all three
  runs say so in their notes), kept for comparability with the 2.10.1 runs.

**Change after round 1:** the pool position becomes a contribution position, banded by the novelty of the
primary claim (the one the paper leads with), plus an evidence adjustment in which routine gaps take at
most −5 in total (`CHANGELOG.md`, 2.13). Had C1, the first listed claim, been marked primary in round 1, the bands would have been
high, medium and incremental, in the human order; whether the panel follows the bands is what round 2 tests.

**Round 2** (contribution position; `evals/iclr2026_terra213_validation_r2.json`, compared with round 1):

| Paper | Human mean | Reviewer pool, r1 → r2 | EIC pool, r1 → r2 | Primary claim (r2) | EIC C, E | Cost |
|-------|-----------:|------------------------|-------------------|--------------------|----------|-----:|
| euMVC1DO4k | 6.0 | 56.4 → 52.6 | 55 → 45 | C2, incremental (30–54) | 53, −8 | $0.42 |
| Lvkbe0CgmZ | 5.0 | 40.6 → 42.6 | 36 → 39 | C1, medium (45–69) | 49, −10 | $0.38 |
| KtocialdxS | 2.67 | 56.2 → 46.0 | 55 → 44 | C1, incremental (30–54) | 50, −6 | $0.67 |

- The lenient case moved as intended (EIC pool −11, all five reviewer pools 42–50).
- The control fell by as much: the Domain Reviewer marked C2 as primary, and its profile changed between
  rounds (C1 high in round 1, medium in round 2). The band amplifies the novelty verdict, including its
  run-to-run variation and the choice of the primary claim.
- On the two empirical papers the EIC took −6 and −8 for gaps the rubric counts as routine (at most −5); on the theory paper, −10 for proof gaps after dropping a claim judged lost.
- The EICs always wrote the two numbers; in two of the three papers, the Phase 1 reports rarely did.
- Order by EIC pool: euMVC1DO4k 45 > KtocialdxS 44 > Lvkbe0CgmZ 39 (human: euMVC1DO4k > Lvkbe0CgmZ >
  KtocialdxS). The per-paper budget guard ran; no run reached its soft limit ($0.70), the highest $0.67.

**Change after round 2:** the primary claim is marked once in the Phase 0 paper memory (the contribution
the abstract leads with) and used by everyone; a missing experiment weakens a claim only when the paper has
no other evidence for it. Round 3 reruns the same papers; with the primary claim fixed, it also shows how much
the profile itself varies between runs.

**Round 3** (primary claim fixed in Phase 0; `evals/iclr2026_terra213_validation_r3.json`, compared with round 2;
the first attempt failed installing the Codex CLI before any API call, and the CLI is now pinned):

| Paper | Human mean | Reviewer pools (r3) | Reviewer pool mean, 2.10.1 / r1 / r2 / r3 | EIC pool, 2.10.1 / r1 / r2 / r3 | Primary (r3) | EIC C, E | Cost |
|-------|-----------:|---------------------|--------------------------------------------|----------------------------------|--------------|----------|-----:|
| euMVC1DO4k | 6.0 | 57, 45, 65, 58, 54 | 60.6 / 56.4 / 52.6 / **55.8** | 59 / 55 / 45 / 45 | C1, incremental | 52, −7 | $0.51 |
| Lvkbe0CgmZ | 5.0 | 45, 51, 59, 50, 43 | 32.6 / 40.6 / 42.6 / **49.6** | 25 / 36 / 39 / 45 | C1, medium | 60, −15 | $0.40 |
| KtocialdxS | 2.67 | 47, 44, 51, 47, 45 | 57.4 / 56.2 / 46.0 / **46.8** | 55 / 55 / 44 / 45 | C1, incremental | 48, −3 | $0.41 |

- The reviewer pools are in the human order for the first time (55.8 > 49.6 > 46.8); in 2.10.1 and rounds 1–2
  the theory paper came last.
- The EIC pools are not: all three are 45. Setting its position afresh, the EIC deducted gaps the reviewers had
  already counted (−7 including "ordinary reporting gaps" on euMVC1DO4k; −15 on Lvkbe0CgmZ).
- With C1 fixed as primary, euMVC1DO4k's primary claim was judged incremental again (a prior robot-learning
  distillation work shares its problem and mechanism), as in round 2; in round 1 it was high. The humans rated
  the paper 6.0; the band caps it at 54.
- No run reached the soft budget limit; the highest was $0.51.

**Change after round 3:** the EIC starts its pool position from the median of the reviewers' pool positions and
moves only for a verified reason; a median above the primary claim's band moves to the band's top unless a delta
the profile missed is verified, and gaps the reviewers already deducted are not deducted again. Applied by hand to
the round 3 reports, this gives 54, 50 and 47, in the human order; round 4 tests whether the EIC does it.

**Round 4** (EIC from the panel median; `evals/iclr2026_terra213_validation_r4.json`, compared with round 3):

| Paper | Human mean | Reviewer pools (r4) | Reviewer pool mean, r3 → r4 | EIC pool, r3 → r4 | Primary (r4) | Cost |
|-------|-----------:|---------------------|-----------------------------|-------------------|--------------|-----:|
| euMVC1DO4k | 6.0 | 47, 49, 51, 49, 45 | 55.8 → 48.2 | 45 → 49 | C1, incremental | $0.55 |
| Lvkbe0CgmZ | 5.0 | 51, 52, 59, 53, 47 | 49.6 → 52.4 | 45 → 52 | C1, medium | $0.58 |
| KtocialdxS | 2.67 | 49, 47, 50, 48, 45 | 46.8 → 47.8 | 45 → 48 | C1, incremental | $0.43 |

- The EIC now follows the panel: each EIC pool is within one point of the reviewers' median, inside the
  primary claim's band, with no gap deducted twice.
- The reviewer instructions did not change between rounds 3 and 4, yet euMVC1DO4k's reviewer pool mean moved
  from 55.8 to 48.2. This is the first, rough measure of run-to-run variation: up to about 8 points per paper,
  as large as the differences between the three papers in rounds 3–4.

**Across the four rounds.** What held in every round from 2 on: the lenient case (KtocialdxS) sits at 46–48
instead of 57 (2.10.1), and the theory paper (Lvkbe0CgmZ) at 43–52 instead of 33. What did not: the control
(euMVC1DO4k, human 6.0) fell from 61 to 48–56, because from round 2 on Terra judged its primary claim
incremental and the band caps it at 54. The three papers now sit within about 46–56, so their order is within
run-to-run variation. The three papers were also used to tune the changes; the next check needs papers the
changes were not tuned on. Total cost of the four rounds at Terra's listed prices: about $5.70.

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

### Full evaluation: 86 papers (skill 2.10.1)

The 86 papers of the full evaluation above (pilot 3's 20 and 66 new), annotated with the same
tool and prompt as the pilot described below: one Sonnet annotator per paper, blind panels,
main issues only. The 66 new papers were annotated after their reviews were finished and the
annotator never saw scores or decisions. Numbers: `evals/iclr2026_issue_overlap_full.json`;
95% bootstrap CIs over papers. The Gap Scout and 2.11 results further down are still from the
20-paper pilot only.

| Hit rate | 86 papers | 66 new papers | Pilot 3 (20) |
|---|---|---|---|
| Human main issues raised by the AI panel | **0.46** [0.42, 0.49] | 0.46 [0.42, 0.50] | 0.45 [0.37, 0.54] |
| … raised by 2+ humans (consensus) | **0.74** [0.67, 0.80] | 0.72 [0.64, 0.80] | 0.78 [0.64, 0.90] |
| … raised by one human | 0.38 [0.34, 0.42] | 0.38 [0.34, 0.42] | 0.38 [0.28, 0.48] |
| … by the panel without the DA | 0.45 [0.42, 0.49] | 0.46 [0.42, 0.49] | 0.44 [0.37, 0.51] |
| AI issues also raised by a human | 0.26 [0.24, 0.28] | 0.26 [0.24, 0.29] | 0.26 [0.22, 0.29] |
| One human's issues raised by the *other* humans | 0.41 [0.36, 0.45] | 0.41 [0.36, 0.45] | 0.39 [0.31, 0.48] |
| One human's issues raised by 1 / 3 / 5 AI reviewers | 0.21 / 0.42 / 0.52 | 0.21 / 0.43 / 0.52 | 0.20 / 0.40 / 0.50 |
| Main issues per paper, human / AI | 11.8 / 20.4 | 11.7 / 20.2 | 12.4 / 20.9 |
| Share raised by one reviewer only, human / AI R1–R4 | 0.77 / 0.73 | 0.77 / 0.73 | 0.77 / 0.73 |

Coverage by k AI reviewers (k = 1–5): 0.18, 0.30, 0.37, 0.42, 0.46. Per role (86 papers):
R1 hits 0.22 of the human issues (0.02 hit by no other role), R2 0.18 (0.08), R3 0.15 (0.06),
R4 0.14 (0.02), DA 0.21 (0.01).

**Importance.** The study has no severity labels, so we use proxies from the human reviews:
how many humans raised the issue, the rating of the reviewers who raised it (ICLR 2026 scale;
≤ 4 is a reject vote), and whether it was one of the first two main points of a review.

| Human main issues (1018) | Issues | Hit rate [95% CI] |
|---|---|---|
| Raised by 2+ humans | 219 | **0.74** [0.67, 0.80] |
| Raised by one human | 799 | 0.37 [0.34, 0.40] |
| Raised by a reviewer who voted reject (≤ 4) | 790 | 0.48 [0.45, 0.52] |
| Raised only by reviewers who voted accept (≥ 6) | 228 | 0.34 [0.28, 0.40] |
| Raised by the paper's lowest-rating reviewer | 555 | 0.50 [0.46, 0.54] |
| One of a reviewer's first two main points | 535 | 0.51 [0.47, 0.56] |
| Not among any reviewer's first two points | 483 | 0.38 [0.34, 0.42] |
| One human, accept votes only, not a lead point | 91 | 0.29 [0.20, 0.38] |

The one issue the AI raised only as a minor point counts as not hit, as in the hit rate above.
"Raised by 2+ humans" counts reviewers who listed the issue as a main point (219); the miss table
below counts any mention, minor points included (221).

Of the hit issues, 63% of the consensus ones and 56% of the single-human ones match an AI issue
that two or more AI reviewers raised: the panel's own agreement tracks importance only weakly.

**By decision** (hit rate; consensus hit rate): accepted (23 papers) 0.39 [0.32, 0.45]; 0.65 —
rejected (43) 0.49 [0.45, 0.54]; 0.80 — withdrawn (17) 0.48 [0.39, 0.58]; 0.76 — desk rejected
(3) 0.42. On accepted papers the humans raise fewer issues (11.0 per paper) and fewer of the
AI's issues match theirs (0.19 vs 0.29 on rejected papers).

**Does the EIC's priority list match the humans' priorities?** Each final report ends with
the EIC's five top concerns. One Sonnet annotator per paper (`evals/gap_match_prompt.md`) saw
the human main issues and, mixed at random without sources, the five top concerns and the
panel's main issues, and matched each human issue to the items that raise the same specific
point (`issue_overlap.py match-prepare` / `match-score`; scoring of the importance tiers in
`evals/iclr2026_issue_overlap_full.json`, `top_concerns`). The re-judged panel hits agree with
the original annotation on 85% of human issues (0.47 vs 0.46).

| | Top concern | Panel main issue |
|---|---|---|
| Items (86 papers) | 430 | 1751 |
| Matches a human main issue | **0.34** [0.30, 0.39] | 0.26 [0.24, 0.28] |
| … a consensus issue (2+ humans) | **0.16** [0.13, 0.19] | 0.10 [0.08, 0.11] |
| … an issue behind a reject vote | 0.29 [0.25, 0.33] | 0.22 [0.19, 0.24] |
| Matches or is related to a human issue | 0.65 [0.61, 0.69] | 0.55 [0.52, 0.57] |

| Human issues the panel raised | Issues | Also among the EIC's top 5 |
|---|---|---|
| Raised by 2+ humans | 161 | **0.45** [0.38, 0.53] |
| Raised by one human | 305 | 0.30 [0.25, 0.36] |
| Behind a reject vote | 384 | 0.37 [0.32, 0.42] |
| Accept votes only | 82 | 0.29 [0.21, 0.38] |
| A reviewer's lead point | 284 | 0.38 [0.33, 0.43] |
| One human, accept votes only, not a lead point | 29 | 0.17 [0.06, 0.31] |

- **Partly.** A top concern is 1.3× as likely as an average panel issue to match a human issue
  and 1.6× as likely to match a consensus issue, and the EIC promotes consensus issues the panel
  found more often than single-reviewer ones (0.45 vs 0.30). The prioritization is aligned with
  the humans', but weakly.
- **Most human priorities are not in the top 5.** The five concerns match 34% of the consensus
  issues (0.74 for the whole panel) and 17% of all human issues; with "related" counted, 55% and
  38%. Each concern bundles several points into one line, which the strict "same specific
  point" criterion often rejects.
- **No order within the five.** Concern #1 matches a human issue 0.37 of the time, #5 0.29, with
  no trend in between (0.30, 0.35, 0.41): the list is a set, not a ranking.
- Two-thirds of the top concerns match no human issue exactly. They are not necessarily wrong,
  but they are what an author reads first.

**What the panel misses (1018 human main issues, 86 papers).** Status: hit 456, related 460,
missed 101, minor only 1. Labels for the 66 new papers by one Sonnet labeler per five papers
(`evals/issue_miss_prompt.md`, as in the pilot); the pilot's labels are reused for its 20.

| Topic | Issues | Hit rate [95% CI] |
|---|---|---|
| Missing experiments, ablations, datasets | 287 | 0.47 [0.41, 0.54] |
| Scope, limitations, generalization | 148 | 0.33 [0.26, 0.41] |
| Method clarity | 107 | 0.22 [0.15, 0.30] |
| Novelty, related work | 100 | 0.60 [0.51, 0.70] |
| Baselines | 99 | 0.63 [0.54, 0.71] |
| Unsupported claims | 91 | 0.37 [0.27, 0.48] |
| Theory | 81 | 0.51 [0.38, 0.63] |
| Efficiency | 50 | 0.64 [0.52, 0.77] |
| Reproducibility | 28 | 0.43 [0.19, 0.67] |
| Presentation | 20 | 0.20 [0.05, 0.39] |

| Evidence needed | Issues | Hit rate |
|---|---|---|
| Paper text and tables | 721 | 0.44 [0.41, 0.48] |
| Outside knowledge (specific prior work, field norms) | 200 | 0.51 [0.44, 0.58] |
| Step-by-step derivation | 52 | 0.40 [0.26, 0.56] |
| Figures or qualitative results | 45 | 0.29 [0.17, 0.42] |

| Likely reason (561 non-hits) | Related | Missed |
|---|---|---|
| AI raised the same area only as a broad category | 242 | 2 |
| AI raised a related concern with a different diagnosis | 107 | 3 |
| Subjective request (more scope, another setting) | 59 | 58 |
| Fine technical or derivation detail | 19 | 21 |
| Needs a specific prior work | 14 | 8 |
| Needs figures or qualitative results | 11 | 6 |
| Unclear | 8 | 3 |

- **The pilot holds.** Every hit-rate number of the pilot is reproduced within 0.06 on the 66
  new papers; the CIs are now about half as wide.
- **Important issues are hit more often.** Consensus issues 0.74 vs 0.37; issues from reject
  votes 0.48 vs 0.34 from accept votes only; a reviewer's lead points 0.51 vs 0.38. The panel
  misses mostly the peripheral issues, not the decisive ones.
- **Granularity, not blind spots.** 82% of the non-hits have a related AI issue; 44% are cases
  where the panel named the area ("more baselines") and the human named the item (91% of those
  human issues are specific). Of the 59 consensus issues not hit, 27 were raised by the panel
  only as a category and 16 with a different diagnosis.
- **Weakest topics**: method clarity (0.22), presentation (0.20) and scope (0.33). Missing
  experiments, the largest topic (28%), is hit 0.47, higher than in the pilot (0.33).
- **Truly missed** (101): mostly subjective scope requests (58) and fine technical detail (21).
- **Caveats**: one LLM annotator and one labeler per paper; importance is inferred from the
  human reviews, not judged; humans saw the figures, the AI read the extracted text; agreement
  with humans is not correctness.

### Pilot 3 details (20 papers)

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

### What the panel misses, and why (pilot, 20 papers)

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
  at about human-human agreement.
- The final rating carries more signal than the plain mean of dimensions. On the full balanced
  set (86 papers) the protocol's regression over the 7 dimensions does worse than the unfitted
  panel rating (test split 0.19 vs 0.45); see "Full evaluation".
- Recognized papers all scored high (EIC 65–70) regardless of outcome; report them separately.
- 20 papers give wide intervals; the full 86-paper evaluation above is the result to cite.
- Issues: on 86 papers the panel raises 46% of the humans' main issues and 74% of those two or
  more humans raised; the more important the issue (consensus, reject vote, lead point), the
  more often it is hit.

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
