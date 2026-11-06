## Phases 1.5, 1.6 and 2 (resumed context, as in the single pipeline)

The five reports are written. Continue in this context, exactly as the skill describes.

**Phase 1.5** (skip it, and say so in the addendum, when the literature check is `off`). As
Reviewer 2 (Domain), run `{SKILL}/scripts/related_search.py` as `references/literature_search.md`
instructs, with `--fp {RES}/phase0/fingerprint.json`, `--mode {LIT}` (cutoff {CUTOFF}), with
`--ledger {RES}/check/search_ledger.jsonl`. At most 12 queries. Write `{RES}/check/R2_addendum.md`.

**Phase 1.6.** As the Synthesizer (Step 0 of `agents/editorial_synthesizer_agent.md`), check every
weakness in the five reports and the addendum against the four tests. Write
`{RES}/check/report_check.md`: the change table, then each report's weaknesses in severity
order. Do not change any score or edit the reports.

Then Phase 2:

