# Split evaluation pipeline

**Status: trial, not adopted.** A 3-paper trial gave no increase in reviewer spread at about
2.2× the cost (see `../REPORT_iclr2026_pilots.md`, "Split pipeline trial"). Evaluation runs
keep `pipeline: single` with skill 2.10. Only the independent check phase is carried into the
next skill version.

The single-agent evaluation (`evals/review_prompt.md`) plays all four reviewers in one
context, so every reviewer after the first has already read the earlier reports. In the
Sonnet pilot the reviewers' composite scores agreed with each other at Spearman 0.88
(human reviewers: 0.12–0.25). This pipeline gives each phase its own fresh `claude -p`
context instead. The skill itself is unchanged.

| Phase | Context gets | Writes |
|---|---|---|
| `phase0` | the unredacted paper, SKILL.md, field analyst, error audit §3 | `phase0/`: card, paper memory, `panel.json`, redacted copy, integrity findings, fingerprint |
| `R1`–`R4` (parallel) | the shared prefix plus its own role file; Read rules deny the other reports, the unredacted paper and the integrity findings; no Bash | `reports/<role>/report.md`, `scores.json` |
| `before` (script, after the reviewers and again after the check) | the four score files and `check/da.json` | `scores_before.json`, `before.json` |
| `check` | the reports, the redacted copy, the fingerprint | `check/R2_addendum.md` (Phase 1.5), `check/report_check.md`, then the Devil's Advocate challenge `check/da.md` and `check/da.json` (Phase 1.6) |
| `eic` | the reports, the check, `before.json`, the integrity findings, then the paper | `eic/decision.md`, `eic/eic.json`, `evidence.json` |
| `finish` (script) | `eic.json` | `scores.json`, `aggregate.json`, `summary.json`, `review.md`, `run.json` |

`summary.json` and `aggregate.json` keep the single-pipeline format, so
`iclr_calibration.py features`, `evaluate` and `pilot` work on these results unchanged.

**Prompt cache.** The shared prefix (skill text, panel card, paper memory, redacted paper;
about 190k characters for a typical paper) is passed with `--append-system-prompt-file`,
and `--exclude-dynamic-system-prompt-sections` moves the per-machine sections out of the
system prompt, so the four reviewer system prompts are byte-identical. The first reviewer
starts `WARMUP` seconds before the others so they read the prefix from the cache.

**Cost log.** `runs/<phase>.json` is each phase's CLI result and `runs/<phase>.wall.json`
its wall time. `run.json` sums cost, turns and tokens (input, output, cache write, cache
read) and keeps the per-phase breakdown.

## Check pipeline (skill 2.11)

`PIPELINE=check` keeps the reviewers in one context, as in the single pipeline, and makes only
the check independent, as the skill's Independent Check does:

| Phase | Context |
|---|---|
| `panel` | one context: Phase 0 and the four reviewers (`panel.md`); the session is kept |
| `check` | fresh: the Report Checker (`agents/report_checker_agent.md`); the unredacted paper and the integrity findings are denied |
| `novelty` | the `panel` session resumed: Phase 1.7, Reviewer 2 may revise Novelty once (`novelty.md`); then `before` again |
| `eic` | the same session resumed (`eic_resume.md` + `eic.md`) |

The output files are the same as the split pipeline's, and `summary.json` records
`"pipeline": "check"`. Compare with skill 2.10 single runs on the same papers.

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
