## This phase: literature check (Phase 1.5) and report check (Phase 1.6)

The five reports are written. Read `{SKILL}/SKILL.md` (Hard Rules, Phases 1.5 and 1.6),
`{SKILL}/references/literature_search.md` and Step 0 of
`{SKILL}/agents/editorial_synthesizer_agent.md`. The paper (redacted copy) is `{COPY}`; the
paper memory is `{RES}/phase0/paper_memory.md`; the reports are
`{RES}/reports/<R1|R2|R3|R4|DA>/report.md`, with the claim IDs in Reviewer 1's `scores.json`.

**Phase 1.5** (skip it, and say so in the addendum, when the literature check is `off`). Act as
Reviewer 2 (Domain). Run `scripts/related_search.py` as `literature_search.md` instructs, with
`--fp {RES}/phase0/fingerprint.json`, `--mode {LIT}` (cutoff {CUTOFF}, set in the fingerprint), with
`--ledger {RES}/check/search_ledger.jsonl`. At most 12 queries. Then write
`{RES}/check/R2_addendum.md`: per-claim novelty verdicts, the novelty delta table, the baseline
scout table, the field snapshot and verified missing references. Only prior peer-reviewed work,
or arXiv-only work 6+ months before the cutoff, can be a required comparison.

**Phase 1.6.** Act as the Synthesizer. Check every weakness in the five reports, and in the
addendum, against the four tests (specific; not already answered by the paper, appendix
included; consistent with the paper; actionable and professional). Write
`{RES}/check/report_check.md`: the table of dropped / rewritten / moved weaknesses with reasons,
then each report's weaknesses in severity order after the check. Do not change any score and
do not edit the reports themselves.

Reply with one line: queries run, weaknesses dropped, rewritten and moved.
