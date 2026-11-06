## This phase: Phase 2 (Synthesizer A, EIC meta-review and decision, Synthesizer B)

Read `{SKILL}/SKILL.md` (Hard Rules, Phase 2), `{SKILL}/agents/editorial_synthesizer_agent.md`,
`{SKILL}/agents/eic_agent.md` (full mode), `{SKILL}/references/editorial_decision_standards.md`,
`{SKILL}/references/quality_rubrics.md` and `{SKILL}/templates/editorial_decision_template.md`.

Inputs, in the order the EIC reads them:
1. The five reports and score files: `{RES}/reports/<R1|R2|R3|R4|DA>/report.md` and `scores.json`.
2. The literature-check addendum and the report check: `{RES}/check/R2_addendum.md`,
   `{RES}/check/report_check.md` (with the checked Gap Scout list; the raw list is
   `{RES}/gaps/gaps.md`).
3. The BEFORE aggregation (plain mean, DA issues provisionally upheld): `{RES}/before.json`.
4. The integrity findings (yours alone): `{RES}/phase0/integrity.json`.
5. The paper, read **after** the reports to check every decisive point: `{PAPER}`
   (unredacted). The paper memory is `{RES}/phase0/paper_memory.md`.

Do what Phase 2 describes: deduplicate and classify issues, give each reviewer a quality weight
(0.5–1.5), rule on every DA-CRITICAL issue with the AC test, take the EIC-weighted mean of the
reviewers' Overall ratings as the starting point, and make the final decision within the DA
ceiling. You may run
`python3 {SKILL}/scripts/aggregate_scores.py <your scores file in {RES}/eic/> --venue {VENUE_KEY} --json`
to check the numbers; the pipeline reruns it from `eic.json` afterwards.

Write to `{RES}/eic/`:
1. `decision.md`: the EIC meta-review, then the Editorial Decision Package and Revision Roadmap
   from the template.
2. `eic.json`:
   ```json
   {
     "final_overall": 1-6,
     "eic_pool_position": 0-100,
     "checker_weights": {"R1": 1.0, "R2": 1.0, "R3": 1.0, "R4": 1.0, "DA": 1.0},
     "eic_weights": {"R1": 1.0, "R2": 1.0, "R3": 1.0, "R4": 1.0, "DA": 1.0},
     "da_rulings": [{"id": "DA-C1", "upheld": true, "resolvable_without_new_data": false}],
     "eic_verification": ["point: Verified/Partly correct/Overstated/Incorrect"],
     "top_concerns": ["one line each, max 5"],
     "recognized": false,
     "injection_found": null,
     "notes": "anything that made the skill hard to follow, ambiguous, or contradictory"
   }
   ```
   `checker_weights` are the base weights from the checks (EIC Step 3, part 1); `eic_weights`
   the final weights after your adjustment. `eic_pool_position` equals the panel pool position
   unless you record a verified correction. One ruling per DA-CRITICAL id in `before.json`. `injection_found` is a quote from
   `integrity.json` or null.

Also write `{RES}/evidence.json`, covering the whole review (the five reports, the addendum and
your decision):
```json
{
  "locations": ["Table 2", "Section 4.3"],
  "quotes": ["exact short phrases (<= 25 words) quoted from the paper"],
  "numbers": [{"claim": "what the number is", "value": "as printed", "derived": false}],
  "references": [{"title": "...", "authors": "...", "year": 2024, "marked_verify": false}]
}
```

Reply with one line: the final Overall and the starting point it came from.
