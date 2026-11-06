# Split evaluation pipeline

**Status: trial, not adopted.** A 3-paper trial gave no increase in reviewer spread at about
2.2× the cost (see `../REPORT_iclr2026_pilots.md`, "Split pipeline trial"). Evaluation runs
keep `pipeline: single`. The independent check is an optional extension from skill 2.12.

The single-agent evaluation (`evals/review_prompt.md`) plays all five reviewers in one
context, so every reviewer after the first has already read the earlier reports. In the
Sonnet pilot the reviewers' composite scores agreed with each other at Spearman 0.88
(human reviewers: 0.12–0.25). This pipeline gives each phase its own fresh `claude -p`
context instead. The skill itself is unchanged.

| Phase | Context gets | Writes |
|---|---|---|
| `phase0` | the unredacted paper, SKILL.md, field analyst, error audit §3 | `phase0/`: card, paper memory, `panel.json`, redacted copy, integrity findings, fingerprint |
| `R1`–`R4`, `DA` (parallel) | the shared prefix plus its own role file; Read rules deny the other reports, the unredacted paper and the integrity findings; no Bash | `reports/<role>/report.md`, `scores.json` |
| `before` (script, after the reviewers) | the five score files | `scores_before.json`, `before.json` |
| `gaps` (optional, `GAPS=1` default) | the redacted copy only | `gaps/gaps.md` (Gap Scout; never shown to the EIC) |
| `check` | the reports, the redacted copy, the fingerprint | `check/checker_estimate.json`, `check/R2_addendum.md` (Phase 1.5), `check/report_check.md` (Phase 1.6), `check/gaps_checked.md` |
| `eic` | the reports, the check, `before.json`, the integrity findings, then the paper | `eic/decision.md`, `eic/eic.json`, `evidence.json` |
| `finish` (script) | `eic.json` | `scores.json`, `aggregate.json`, `summary.json`, `review.md`, `run.json` |

`summary.json` and `aggregate.json` keep the single-pipeline format, so
`iclr_calibration.py features`, `evaluate` and `pilot` work on these results unchanged.

**Prompt cache.** The shared prefix (skill text, panel card, paper memory, redacted paper;
about 190k characters for a typical paper) is passed with `--append-system-prompt-file`,
and `--exclude-dynamic-system-prompt-sections` moves the per-machine sections out of the
system prompt, so the five reviewer system prompts are byte-identical. The first reviewer
starts `WARMUP` seconds before the others so they read the prefix from the cache.

**Cost log.** `runs/<phase>.json` is each phase's CLI result and `runs/<phase>.wall.json`
its wall time. `run.json` sums cost, turns and tokens (input, output, cache write, cache
read) and keeps the per-phase breakdown.

## Check pipeline (skill 2.12, optional extensions)

`PIPELINE=check` keeps the five reviewers in one context, as in the single pipeline, and runs
the two optional extensions in fresh contexts:

| Phase | Context |
|---|---|
| `panel` | one context: Phase 0 and the five reviewers (`panel.md`); the session is kept |
| `gaps` | fresh (skipped with `GAPS=0`): the Gap Scout reads the redacted copy only |
| `check` | fresh: the Report Checker (`agents/report_checker_agent.md`); the unredacted paper and the integrity findings are denied |
| `eic` | the `panel` session resumed (`eic_resume.md` + `eic.md`); the Gap Scout list and the checker's estimate are denied |

The output files are the same as the split pipeline's, and `summary.json` records
`"pipeline": "check"` and the checker's estimate. Skill 2.11 runs (four reviewers, the
Devil's Advocate in `check/da.md`, Phase 1.7 `novelty`) are still read by `run_split.py
before`/`finish` and `issue_overlap.py`.

## Running

From the repository root, with `evals/work/papers/<id>/blinded.txt` in place:

```bash
CUTOFF=2025-09-24 evals/split/run_paper.sh <id>
```

Defaults: `MODEL=claude-sonnet-5-5`, `EFFORT=high`, `BUDGET=3` (USD cap per phase, API
only), `LIT=strict`, `WARMUP=20`. Authentication is whatever the `claude` CLI has: a
local login or `CLAUDE_CODE_OAUTH_TOKEN` uses a subscription, `ANTHROPIC_API_KEY` bills
the API.

In GitHub Actions, set `"pipeline": "split"` in the run config (and `"auth": "subscription"`
with a `CLAUDE_CODE_OAUTH_TOKEN` secret to avoid API billing). The default stays
`single`. Nothing runs until a run is dispatched or `evals/iclr_run.json` changes.

`tests/test_split_pipeline.py` checks the prompts, the shared prefix (redacted, no
integrity findings), the deny rules and the `before`/`finish` steps without calling a model.
