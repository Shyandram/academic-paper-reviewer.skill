## This phase: literature check (Phase 1.5), report check and Devil's Advocate challenge (Phase 1.6)

The four reports are written. You are the **Report Checker**: a fresh context that did not
write them. Read `{SKILL}/agents/report_checker_agent.md`, `{SKILL}/SKILL.md` (Hard Rules,
"Independent Check", Phases 1.5 and 1.6), `{SKILL}/references/literature_search.md` and
Section 5 (error log and precision rules) of `{SKILL}/references/error_audit.md`. The paper (redacted copy) is `{COPY}`; the
paper memory is `{RES}/phase0/paper_memory.md`; the reports are
`{RES}/reports/<R1|R2|R3|R4>/report.md`, with the claim IDs in Reviewer 1's `scores.json`.

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

**Phase 1.6.** Check every weakness in the four reports, and in the addendum, with the five
tests in `report_checker_agent.md` (specific; not already answered by the paper, appendix
included; consistent with the paper; actionable and professional; factually accurate). For
test 5, open each cited location in `{COPY}` and recount. Write `{RES}/check/report_check.md`
in the format the role file gives: the change table, the factual error list, each report's
weaknesses in severity order after the check, and the per-reviewer test counts. Do not change
any score and do not edit the reports themselves.

**Gap Scout list.** Also check `{RES}/gaps/gaps.md` (if present) as `report_checker_agent.md`
says: drop items the paper already answers or contradicts, mark each kept item with the panel
weakness that covers it or `new`, and add the result to `report_check.md` under
`## Anticipated Reviewer Concerns`, keeping the Scout's order and IDs.

**Devil's Advocate challenge (last).** After the check, read
`{SKILL}/agents/devils_advocate_reviewer_agent.md` and run the challenge as it says: steelman,
core argument chain, strongest counter-argument, then CRITICAL issues and at most 5 MAJOR (no
MINOR), each naming the chain step it attacks. Do not repeat weaknesses the checked reports
already raise; cite them by ID when they bear on the chain. Run its protocol sweep, claim
distortion check and numerical sanity check on `{COPY}`. No scores. Write
`{RES}/check/da.md` in that file's format, and `{RES}/check/da.json`:
`{"da_critical": [{"id": "DA-C1", "summary": "one line", "resolvable_without_new_data": false}],
"da_major": [{"id": "DA-M1", "summary": "one line"}]}` (empty lists when there are none; most
papers have no CRITICAL issue).

Reply with one line: queries run, weaknesses dropped, rewritten and moved, factual errors,
DA-CRITICAL and DA-MAJOR counts.
