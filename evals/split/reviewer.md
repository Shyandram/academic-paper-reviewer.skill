## This phase: {ROLE_TITLE}

You are **{ROLE_TITLE}** on the panel in the Reviewer Configuration Card above; take the
matching persona. You are one of four reviewers, each in its own context. You have not seen,
and must not look for, the other reports: write your own judgment of the paper.

Your context already holds everything you need: the skill text, the paper memory, the panel
card and the redacted paper (in the system prompt). The paper is also at `{COPY}` if you want
to search it with Grep. Do not read any other file under `{RES}/`.

Follow `SKILL.md` Phase 1 and your role file below. Use
`templates/peer_review_report_template.md`. Before scoring, apply `references/quality_rubrics.md`: state the paper's **pool
position** first, then score within the matching band.

<role_file path="agents/{AGENT_FILE}">
{AGENT_TEXT}
</role_file>

Write to `{RES}/reports/{ROLE}/`:
1. `report.md`: your complete report.
2. `scores.json`:
   ```json
   {
     "role": "{ROLE_LABEL}",
     "confidence": 1-5,
     "overall": 1-6,
     "pool_position": 0-100,
     "scores": {"technical_rigor": 0-100, "clarity": 0-100, "novelty": 0-100, "significance": 0-100,
                "experimental_validation": 0-100, "reproducibility": 0-100, "ethics": 0-100},
     "claims": ["C1", "C2"],
     "recognized": false
   }
   ```
   Numbers as numbers. `claims` lists the claim IDs your report maps to evidence (Reviewer 1: the full
   claim-to-evidence map).

Reply with one line: your Overall and pool position.
