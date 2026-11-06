## This phase: Phase 0 (field analysis, panel, paper memory)

Read `{SKILL}/SKILL.md` (the Hard Rules and "Phase 0"), `{SKILL}/agents/field_analyst_agent.md`
and Section 3 of `{SKILL}/references/error_audit.md`. Then read the complete paper:
`{PAPER}`.

Run, in this order:
1. `python3 {SKILL}/scripts/integrity_scan.py --paper {PAPER} --json --redact {RES}/phase0/reviewer_copy.txt > {RES}/phase0/integrity.json`
   The findings are for the EIC only. Do not mention them in any file below.
2. If the literature check is not `off`:
   `python3 {SKILL}/scripts/related_search.py fingerprint --paper {PAPER} --out {RES}/phase0/fingerprint.json`,
   then complete the fingerprint as `references/literature_search.md` describes (title, method
   names, identifiers, distinctive phrases, cutoff date {CUTOFF}).

Write to `{RES}/phase0/`:
- `card.md`: the Reviewer Configuration Card (discipline, paper type, venue tier and maturity,
  four fictional reviewer personas plus the EIC, each with its focus) and any assumptions.
- `paper_memory.md`: the paper memory exactly as Section 3 of `error_audit.md` defines it
  (claims C1, C2, … with locations; setup facts, each located or "not stated"; headline numbers
  with source tables; appendix and supplement summary; unverifiable parts). Facts only, no
  judgments: all four reviewers receive it.
- `panel.json`: `{"paper_type": "<empirical|theoretical|dataset|system|benchmark|analysis|position>", "field": "...", "venue_tier": "...", "recognized": false}`

Do not review the paper or score it. Reply with one line: the paper type and the field.
