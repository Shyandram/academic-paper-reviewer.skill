# Academic Paper Reviewer for Codex and Claude

A multi-perspective peer-review skill for Codex and Claude, tuned for **computer vision, deep learning and ML** papers but usable in any field. It simulates a full editorial process: four independent reviewers, an unscored Gap Scout, an independent Report Checker that also runs a Devil's Advocate challenge, then an Editor-in-Chief who acts as area chair. The EIC reads every review, checks the decisive points against the paper, weights each reviewer by the quality of their review, and makes the final decision. Scores are aggregated reproducibly as two lists (the reviewers' official scores and the EIC's internal weighted assessment), and the skill turns the result into a prioritized revision plan, a rebuttal draft, or a verification of your revisions.

```
You:    Review this paper for CVPR: [attach PDF]
Agent:  📋 Paper analysis + 5-reviewer configuration card → 5 independent reports
        → EIC meta-review: reviewer weights, official scores and the EIC's internal weighted assessment, final decision
        → Editorial decision letter, consensus map, Revision Roadmap
```

> The output is a **simulation** to help you strengthen a paper. It is not a prediction of any venue's decision.

**Project page:** <https://shyandram.github.io/academic-paper-reviewer.skill/> · **Current version:** 2.11 ([changelog](CHANGELOG.md))

---

## Features

| Mode | Say something like | You get |
|------|-------------------|---------|
| **full** (default) | "Review this paper" | 4 reports (Methodology, Domain, Perspective, Generalist) + Gap Scout checklist + report check and Devil's Advocate challenge + EIC meta-review + Editorial Decision + Revision Roadmap |
| **quick** | "Is my paper ready for submission?" | EIC quick assessment + submission-readiness check (anonymity, page limit, checklists…) |
| **methodology-focus** | "Are my baselines fair?" / "Check my experiments" | Claim-to-evidence map, fairness-of-comparison audit, statistics audit, prioritized fixes with compute estimates |
| **guided** | "Walk me through the review" | Socratic, one-issue-at-a-time dialogue |
| **rebuttal** | "Help me write the rebuttal" + the reviews | Triage of every point + a draft in the venue's format (one-page PDF or OpenReview comments) |
| **re-review** | "Check whether my revision addresses the reviews" | Item-by-item verification (FULLY / PARTIALLY / NOT ADDRESSED / MADE WORSE) + a new decision |

What sets it apart:
- **Field-aware panel.** Reviewers are configured from the paper's actual sub-field and technique (e.g., "token pruning + latency benchmarking" rather than "deep learning").
- **CV/ML depth.** Task-specific checklists cover detection, segmentation, 3D/NeRF/3DGS, restoration, generation, VLMs, video, medical imaging and efficient models. They target the confounds that matter in practice: backbone, pretraining data, resolution, schedule, TTA and latency methodology.
- **Devil's Advocate with teeth, and an EIC who checks it.** After the report check, the Report Checker runs a Devil's Advocate challenge in its fresh context (no scores, no vote): it steelmans the paper, gives the strongest counter-argument and recomputes headline numbers. The EIC checks each CRITICAL issue against the paper with an area-chair test ("would I reject on this alone?"). Only issues that are truly fatal cap the decision.
- **Two score lists.** The **official** list holds the reviewers' raw ratings and scores and their plain means: what authors see, never modified. The **EIC assessment** is the EIC's internal view, weighting each reviewer by confidence × a quality weight (0.5–1.5); it can be higher or lower than the official one. The decision starts from the **EIC-weighted mean of the reviewers' Overall ratings**, like an area chair weighing recommendations. The 0–100 dimension composite is a cross-check, and the EIC must explain any disagreement.
- **Calibrated to the submission pool.** Each reviewer, and the EIC, first states the paper's *pool position*: the share of the venue's submissions it is better than, using the venue's real acceptance rate (about 25% at the major ML/CV conferences). They then score within the matching band. The bar is what the venue actually accepts, not a flawless paper, and uncertainty is never a reason to call a paper borderline. See [Evaluation](#evaluation).
- **Reproducible scoring.** `scripts/aggregate_scores.py` computes confidence-weighted scores, paper-type composites, spread flags, the DA cap and consistency warnings.
- **Venue-aware scoring.** It covers 11 venues: **CVPR, ICCV, ECCV, NeurIPS, ICLR, ICML, AAAI, ACM MM, TMLR, IEEE TPAMI and IEEE TIP**. Scores are translated into each venue's own form, for example ICLR Soundness/Presentation/Contribution and rating, the ICML 1–5 recommendation, the TMLR Yes/No criteria, or IEEE journal recommendations. A **Cross-Venue Outlook** shows how the same paper would likely fare at each venue. Every scale is labeled *official*, *confirmed*, *secondary*, *assumed* or *unpublished*, so nothing unverified is presented as official.
- **Literature check without self-leaks.** With network access, reviewers search arXiv for related work and verify every recommended reference. A fingerprint filter refuses queries that could find the reviewed paper, drops the paper's own arXiv versions, code pages, reviews and acceptance lists unread, and labels the rest prior (peer-reviewed or 6+ months old) / recent preprint / concurrent / newer; only prior work can be a required comparison. The check runs after the reviewers have read the full paper. Every decision is logged (`literature check: on | strict | off`). Searches are driven by the paper's contribution claims and its benchmarks: each claim gets a novelty verdict with supporting papers, a **baseline scout** lists prior methods reported on the same benchmarks (and baselines the paper under-reports), a coverage check drives a second round of searches, and a short field snapshot calibrates significance. A **similarity check** then ranks the closest prior works (novelty is argued against them, in a delta table) and flags verbatim text overlap as an integrity concern for the editor, never as an accusation.
- **Error audit with precision rules.** The Methodology Reviewer hunts for concrete errors in nine categories (result inconsistencies, equation/proof errors, assumptions, protocol flaws, claim distortion, inconsistent definitions, citation errors, omissions, figure/table integrity). It works claim by claim from a shared factual *paper memory* and sweeps for omissions. Every error needs a location, a verbatim quote and a concrete check; suspicions become questions. Before the EIC reads anything, an independent **Report Checker** (a fresh context when the host allows delegation) removes vague weaknesses, points the paper already answers, and claims the paper contradicts, re-checks every number, count, quote and attribution against the paper, and groups cosmetic issues as Minor.
- **Anticipated reviewer concerns.** An unscored **Gap Scout**, in its own context and reading only the paper, lists the 20–30 concrete weaknesses reviewers are most likely to raise: the specific missing experiment, baseline, definition or setting. On 20 ICLR 2026 submissions it raised 65% of the human reviewers' main issues alone, and 73% together with the panel (47% for the panel alone). The final report includes it as a checklist.
- **Prompt-injection safe.** The manuscript is data, never instructions. `scripts/integrity_scan.py` flags text addressed to reviewers or AI systems ("ignore previous instructions…") and hidden characters. Findings go to the editor as integrity concerns and never raise a score.
- **Integrity guardrails.** No fabricated citations, fictional reviewer personas only, a confidentiality reminder for assigned reviewers, and every point tied to a location in the manuscript.

---

## Installation

The packaged skill is the file `academic-paper-reviewer.skill`, a zip archive that contains the `academic-paper-reviewer/` folder.

### Codex (CLI, IDE, and cloud tasks)

From the repository root, install a project-local skill:

```bash
python3 tools/install_codex_skill.py
```

This creates `.agents/skills/academic-paper-reviewer`, a relative symlink to the
source. It is repeatable and refuses to replace existing files or another skill.
Keep this checkout in place while using the link. For a personal installation:

```bash
python3 tools/install_codex_skill.py --skills-dir ~/.agents/skills
```

Start a new Codex session in this repository and invoke
`$academic-paper-reviewer Review /absolute/path/paper.pdf for CVPR`.
Discovery depends on the host; installing during a session may require a new
session. If the host does not discover local skills, ask Codex to read
`academic-paper-reviewer/SKILL.md` and follow it directly. Cloud tasks can use
this fallback immediately. No API key or running server is required.

PDF text extraction and page rendering are optional capabilities (for example,
Poppler's `pdftotext` and `pdftoppm`); see
[Codex runtime guidance](academic-paper-reviewer/references/codex_runtime.md).
Five role-based passes work without subagents; parallel execution is used only
when supported and permitted by the host.

### Claude apps (claude.ai web / desktop)

1. Download `academic-paper-reviewer.skill` from this repository.
2. In Claude, open **Settings → Capabilities** and make sure code execution / skills are enabled.
3. Under **Skills**, choose **Upload skill** and select the `.skill` file. If the uploader asks for a `.zip`, rename the file to `academic-paper-reviewer.zip`; it is the same format.
4. Start a new chat and say *"Review this paper"* with a PDF attached.

*Menu names change over time. If you can't find them, see Anthropic's help center article on using Skills in Claude.*

### Claude Code

Personal install (available in every project):

```bash
git clone https://github.com/shyandram/academic-paper-reviewer.skill.git
mkdir -p ~/.claude/skills
cp -r academic-paper-reviewer.skill/academic-paper-reviewer ~/.claude/skills/
```

Project install (shared with your collaborators through the repo):

```bash
mkdir -p .claude/skills
cp -r /path/to/academic-paper-reviewer.skill/academic-paper-reviewer .claude/skills/
```

Or unzip the packaged file directly:

```bash
unzip academic-paper-reviewer.skill -d ~/.claude/skills/
```

Claude Code discovers skills at startup. Restart the session, then ask *"review paper.pdf"*. In Claude Code the four reviewers and the Gap Scout can run as parallel subagents, which keeps them independent.

### Claude API (Agent Skills)

Upload the `academic-paper-reviewer/` folder through the Skills API and attach the skill to requests that use the code-execution tool. See Anthropic's Agent Skills documentation for the current endpoints and beta headers.

### Requirements

- None for normal use. Everything is Markdown instructions.
- `scripts/aggregate_scores.py` needs **Python 3.8+**, standard library only. Without code execution, the agent follows the same formulas by hand.

---

## Usage Examples

```
Review this paper: [attach PDF]
Quick look — is this ready for ECCV? [attach PDF]
Check my experiments only. Target venue: NeurIPS. [attach PDF]
Here are my three CVPR reviews. Help me write the one-page rebuttal. [paste reviews + attach paper]
Re-review: here is the revised manuscript and our response letter. [attach both]
Review this paper in English, anonymous reviewers, skip confirmation.
Guide me through reviewing this paper — I'm learning to review.
Compare this paper across CVPR, ICLR and TMLR — which venue fits best?
Review for ICLR in venue format.
```

Useful modifiers: `target venue: …`, `journal: TPAMI`, `compare venues`, `venue format`, `skip confirmation`, `anonymous reviewers`, `in English`, `save to file`.

### Supported venues

| Key | Venue | Scale used | Status |
|-----|-------|-----------|--------|
| `cvpr` / `iccv` / `eccv` | CVPR, ICCV, ECCV | 6-point (Accept · Weak Accept · Borderline Accept · Borderline Reject · Weak Reject · Reject); ECCV judged against the declared contribution type | confirmed |
| `neurips` | NeurIPS | Quality/Clarity/Significance/Originality 1–4, Overall 1–6 | secondary |
| `iclr` | ICLR | Soundness/Presentation/Contribution 1–4, rating {0,2,4,6,8,10} (legacy {1,3,5,6,8,10}) | secondary |
| `icml` | ICML | Overall recommendation 1–5 (2025) | official |
| `aaai` | AAAI | 1–10 (6 Borderline accept · 5 Borderline reject · 4 Weak reject …) + Phase-1 early-rejection risk | confirmed |
| `acmmm` | ACM Multimedia | Generic + multimedia-scope gate | unpublished |
| `tmlr` | TMLR | Claims & evidence / Audience interest (Yes/No) | official |
| `tpami` / `tip` | IEEE TPAMI / TIP | Accept · Minor · Major · (Revise &) Resubmit · Reject | secondary / assumed |

Venue forms change every year. Check `references/venue_profiles.md` and the venue's current guidelines, and update `scripts/venues.json` when a form changes.

### Scoring by hand or in CI

```bash
python3 academic-paper-reviewer/scripts/aggregate_scores.py academic-paper-reviewer/scripts/example_scores.json
python3 academic-paper-reviewer/scripts/aggregate_scores.py scores.json --json
python3 academic-paper-reviewer/scripts/aggregate_scores.py scores.json --venue cvpr --venue tmlr
python3 academic-paper-reviewer/scripts/aggregate_scores.py scores.json --all-venues
```

---

## Evaluation

[`evals/`](evals/) holds the evaluation tools and reports.

- **Accepted papers** ([`evals/REPORT.md`](evals/REPORT.md)): 30 recently accepted ICLR/CVPR/ECCV papers, with grounding checks, planted-flaw controls and consistency checks.
- **ICLR 2026 calibration** ([`evals/REPORT_iclr2026_pilots.md`](evals/REPORT_iclr2026_pilots.md)) follows the [paperreview.ai protocol](https://paperreview.ai/tech-overview):
  - sample ICLR submissions with human scores;
  - fit a linear map from the 7 dimension scores on a train split;
  - report Spearman with a human score and acceptance AUC on the test split, with and without withdrawn papers.

  Reviewers get anonymized arXiv versions posted before the decision, and never see human scores or decisions. The literature check runs in `strict` mode with the submission deadline as cutoff.

Pilot on 20 stratified ICLR 2026 submissions, all using the final rating:

| Run | Spearman with mean human rating [95% CI] | Acceptance AUC |
|---|---|---|
| Haiku, default effort | +0.20 [−0.21, +0.58] | 0.56 |
| **Sonnet, high effort** | **+0.48 [+0.09, +0.74]** | **0.67** |
| Human vs human (2026 test split) | 0.25 | 0.75 |
| paperreview.ai (ICLR 2025, AI vs human) | 0.42 | 0.75 |

This is a pilot, not a result. With 20 papers the intervals are wide, and the full balanced evaluation is still pending. Model capability matters: Haiku's scores did not separate papers. Use a strong model at high effort for scoring.

**Running it.** `.github/workflows/iclr-calibration.yml` reviews papers through the API using the repository secret `ANTHROPIC_API_KEY`. Every paper costs money (about $2 with Sonnet at high effort), so start with a small pilot. Configure a run in `evals/iclr_run.json`:

```json
{"mode": "review", "pick": "stratified", "limit": 20, "model": "claude-sonnet-5-5",
 "effort": "high", "max_parallel": 10, "budget": 6}
```

Then push `evals/iclr_run.json` on a branch listed in the workflow's `push` trigger. You can also start the workflow manually (`workflow_dispatch`), but the manual form has no `effort` field, so use the JSON file when you need that setting. A run with `{"mode": "evaluate", "runs": [...]}` collects earlier review runs and computes the metrics. To work locally, `python3 evals/iclr_calibration.py --help` lists the steps: `sample`, `find`, `sources`, `fetch`, `features`, `evaluate`. Manuscripts and review text stay in the ignored `evals/work/`; only scores and paper IDs are committed. To compare the panel's weaknesses with the human reviews (issue overlap and hit rate), run `python3 evals/issue_overlap.py prepare` on the fetched reviews and results, annotate each paper with `evals/issue_overlap_prompt.md`, then `python3 evals/issue_overlap.py analyze` (and `misses` / `categories` with `evals/issue_miss_prompt.md` for what the panel misses, `match-prepare` / `match-score` with `evals/gap_match_prompt.md` for the Gap Scout); results for the 20-paper pilot are in `evals/REPORT_iclr2026_pilots.md`.

## Repository Layout

```
academic-paper-reviewer.skill          ← packaged skill (zip), the file you install
academic-paper-reviewer/               ← skill source
├── SKILL.md                           ← entry point: modes, workflow, hard rules
├── agents/                            ← one file per role
│   ├── field_analyst_agent.md         (Phase 0: panel configuration)
│   ├── eic_agent.md                   (EIC meta-reviewer: final decision; quick, re-review, coaching)
│   ├── generalist_reviewer_agent.md   (R4: venue fit, presentation)
│   ├── methodology_reviewer_agent.md  (R1; methodology-focus mode)
│   ├── domain_reviewer_agent.md       (R2)
│   ├── perspective_reviewer_agent.md  (R3)
│   ├── devils_advocate_reviewer_agent.md
│   ├── report_checker_agent.md        (Phases 1.5–1.6: independent literature and report check)
│   ├── editorial_synthesizer_agent.md (Phase 2)
│   └── rebuttal_strategist_agent.md   (rebuttal mode)
├── references/                        ← rubrics, standards, checklists, venue profiles
├── templates/                         ← report, decision, rebuttal, response-letter formats
├── scripts/aggregate_scores.py        ← score aggregation + venue views (+ example_scores.json)
├── scripts/integrity_scan.py          ← Phase 0 scan for text addressed to reviewers/AI (prompt injection)
├── scripts/related_search.py          ← literature check: fingerprint, concept search, self-exclusion filter, verify, baseline scout, coverage, similarity, claim-level novelty profile
├── scripts/venues.json                ← venue profiles (emphasis, bar, scale, form fields)
└── examples/                          ← worked, fully fictional examples
tools/install_codex_skill.py           ← safe, repeatable Codex installation
tools/build_skill.py                   ← validate + package the skill
evals/                                 ← evaluation tools, run configs and reports (see Evaluation)
.github/workflows/                     ← ICLR calibration runs and an API smoke test
tests/                                 ← unit tests for the scoring script and the evaluation tools
```

## Development

```bash
python3 -m unittest discover -s tests     # test the scoring script and evaluation tools
python3 tools/build_skill.py --check      # validate frontmatter, file references, script
python3 tools/build_skill.py              # validate and rebuild academic-paper-reviewer.skill
```

Edit files under `academic-paper-reviewer/`, then rebuild. Commit the source and the rebuilt `.skill` together. The build is deterministic, so an unchanged source gives a byte-identical archive.

## Responsible Use

- Intended for authors improving their own work, for training reviewers, and for feedback given with the authors' consent.
- **If you are an assigned reviewer**, check your venue's policy before putting a confidential submission into any AI tool. Many CV/ML venues restrict or forbid it.
- Reviewer personas are fictional. Recommended references follow a no-fabrication rule, but **verify every citation** before you use it.
- Venue rules (page limits, rebuttal formats, score scales) change yearly. `references/venue_profiles.md` is a guide, not a substitute for the current call for papers.

## Changelog

See [CHANGELOG.md](CHANGELOG.md).
