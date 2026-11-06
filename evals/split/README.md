# Split evaluation pipeline

**Status: trial, not adopted.** A 3-paper trial gave no increase in reviewer spread at about
2.2× the cost (see `../REPORT_iclr2026_pilots.md`, "Split pipeline trial"). Evaluation runs
keep `pipeline: single`. The independent check is an optional extension from skill 2.10.1.

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
| `check` | the reports, the redacted copy, the fingerprint | `check/R2_addendum.md` (Phase 1.5), `check/report_check.md` (Phase 1.6) |
| `eic` | the reports, the check, `before.json`, the integrity findings, then the paper | `eic/decision.md`, `eic/eic.json`, `evidence.json` |
| `finish` (script) | `eic.json` | `scores.json`, `aggregate.json`, `summary.json`, `review.md`, `run.json` |
| post-review (optional, below) | | `post/`, `gaps/`; `finish` runs again |

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

## Check pipeline (skill 2.10.1)

`PIPELINE=check` runs the review as the single pipeline does, in one context:

| Phase | Context |
|---|---|
| `panel` | one context: Phase 0 and the five reviewers (`panel.md`); the session is kept |
| `eic` | the `panel` session resumed: Phases 1.5 and 1.6 (`eic_resume.md`), then Phase 2 (`eic.md`) |

`summary.json` records `"pipeline": "check"`.

## Post-review analysis (both pipelines)

After `finish`, the optional analyses run, each in a fresh context that cannot change the
review; `finish` then runs again to add them to `review.md` and `summary.json`:

| Phase | Context | Writes |
|---|---|---|
| `estimate` (`EST=0` skips) | the redacted copy only; every result file denied | `post/checker_estimate.json` |
| `gaps` (`GAPS=0` skips) | the redacted copy only; every result file denied | `gaps/gaps.md` |
| `post` (`POST=0` skips) | the finished review and the redacted copy; edits to the review denied | `post/fact_check.md`, `post/gaps_checked.md` |

Skill 2.11 runs (four reviewers, the Devil's Advocate in `check/da.md`, the estimate in
`check/`) are still read by `run_split.py before`/`finish` and `issue_overlap.py`.

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
