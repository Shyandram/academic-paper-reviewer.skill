## This phase: literature check (Phase 1.5) and report check (Phase 1.6), optional Report Checker

The five reports are written. You are the **Report Checker**: a fresh context that did not
write them. Read `{SKILL}/agents/report_checker_agent.md`, `{SKILL}/SKILL.md` (Hard Rules,
Phases 1.5 and 1.6, "Optional Extensions"), `{SKILL}/references/literature_search.md` and
Section 5 (error log and precision rules) of `{SKILL}/references/error_audit.md`. The paper
(redacted copy) is `{COPY}`; the paper memory is `{RES}/phase0/paper_memory.md`; the reports are
`{RES}/reports/<R1|R2|R3|R4|DA>/report.md`, with the claim IDs in Reviewer 1's `scores.json`.

**First, the independent estimate.** Before opening any report or score file, read `{COPY}`
and write `{RES}/check/checker_estimate.json`:
`{"pool_position": 0-100, "overall": 1-6, "reasons": "<2-3 sentences>"}`, as
`report_checker_agent.md` describes. Do not change it after reading the reports.

**Phase 1.5** (skip it, and say so in the addendum, when the literature check is `off`). Act as
Reviewer 2 (Domain). Run `scripts/related_search.py` as `literature_search.md` instructs, with
`--fp {RES}/phase0/fingerprint.json`, `--mode {LIT}` (cutoff {CUTOFF}, set in the fingerprint), with
`--ledger {RES}/check/search_ledger.jsonl`. At most 12 queries. Then write
`{RES}/check/R2_addendum.md`: per-claim novelty verdicts, the novelty delta table, the baseline
scout table, the field snapshot and verified missing references. Only prior peer-reviewed work,
or arXiv-only work 6+ months before the cutoff, can be a required comparison.

**Phase 1.6.** Check every weakness in the five reports, and in the addendum, with the five
tests in `report_checker_agent.md` (specific; not already answered by the paper, appendix
included; consistent with the paper; actionable and professional; factually accurate). For
test 5, open each cited location in `{COPY}` and recount. Write `{RES}/check/report_check.md`
in the format the role file gives: the change table, the factual error list, each report's
weaknesses in severity order after the check, and the per-reviewer test counts. Do not change
any score and do not edit the reports themselves.

**Gap Scout list** (only if `{RES}/gaps/gaps.md` exists). Check it as `report_checker_agent.md`
says: drop items the paper already answers or contradicts, mark each kept item with the panel
weakness that covers it or `new`, and write the result to `{RES}/check/gaps_checked.md` under
`## Anticipated Reviewer Concerns`, keeping the Scout's order and IDs. It is not for the EIC.

Reply with one line: queries run, weaknesses dropped, rewritten and moved, factual errors.
