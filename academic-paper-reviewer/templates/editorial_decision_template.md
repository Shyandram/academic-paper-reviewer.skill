# Editorial Decision Template

## Full Review Decision

```markdown
# Editorial Decision

## Paper: [Full title]
## Submission ID: [if available]
## Date: [YYYY-MM-DD]
## Target Venue: [venue] | Paper Type: [type]
## Review Team (fictional personas): [5 reviewers with roles]

---

## Decision: [Strong Accept (6) / Accept (5) / Borderline Accept (4) / Borderline Reject (3) / Reject (2) / Strong Reject (1)]

---

## Score Summary

### Aggregated Dimension Scores (Confidence-Weighted)

*Paste the markdown output of `python3 scripts/aggregate_scores.py scores.json` here, or fill in the table by hand with the same formulas.*

| Dimension | EIC | R1 (Meth.) | R2 (Domain) | R3 (Persp.) | DA | Weighted Avg | Spread |
|-----------|-----|------------|-------------|-------------|-----|-------------|--------|
| Technical Rigor | | | | | | | |
| Clarity & Presentation | | | | | | | |
| Novelty & Originality | | | | | | | |
| Significance & Impact | | | | | | | |
| Experimental Validation | | | | | | | |
| Reproducibility | | | | | | | |
| Ethical Compliance | | | | | | | |
| **Composite** | | | | | | **[avg]** | |

**Composite-implied decision**: [n] | **DA cap**: [none / 4 / 3] | **Final decision**: [n] ([reason if it differs from the composite band])
**Journal recommendation** (if journal target): [Accept / Minor Revision / Major Revision / Reject]

### NeurIPS-Style Scores (EIC Final)

| Dimension | Score |
|-----------|-------|
| Quality | [1–4] |
| Clarity | [1–4] |
| Significance | [1–4] |
| Originality | [1–4] |
| **Overall** | **[1–6]** |
| Confidence | [1–5] |

---

## Editorial Decision Letter

Dear Authors,

Thank you for submitting your paper "[Title]" to [venue].

[1–2 sentences acknowledging the paper's topic and ambition.]

**Overall Assessment:**
[2–3 sentences summarizing the reviewers' collective view. Lead with strengths.]

**Key Strengths Identified by Reviewers:**
1. [Strength — cite which reviewer(s)]
2. [Strength]
3. [Strength]

**Key Concerns Requiring Attention:**
1. [Concern — cite which reviewer(s), note if CONSENSUS or SPLIT]
2. [Concern]
3. [Concern]

[If Devil's Advocate raised CRITICAL issues:]
**Critical Challenge (Devil's Advocate):**
[Summarize the DA's strongest objection. Explain why it must be addressed.]

**Decision: [Decision]**

[Decision-specific paragraph:]
- If Accept/Strong Accept: Congratulations. [Note any minor suggestions.]
- If Borderline Accept: [Explain what tipped the balance. Note conditions if any.]
- If Borderline Reject: [Explain what would need to change for acceptance.]
- If Reject/Strong Reject: [Explain the primary reasons. Be constructive.]

[If revision requested:]
Please refer to the Revision Roadmap below for prioritized guidance.

Sincerely,
[EIC Name]
Editor-in-Chief

---

## Consensus and Disagreement Map

### Points of Consensus (3+ reviewers agree)
| Issue | Reviewers | Classification |
|-------|-----------|---------------|
| [issue] | [R1, R2, R3...] | CONSENSUS-[N] |

### Points of Disagreement
| Issue | For | Against | Arbitration |
|-------|-----|---------|-------------|
| [issue] | [reviewers] | [reviewers] | [EIC's reasoning] |

### Score Spread Discussion
[For each dimension flagged ⚠ (spread > 20): which reviewers diverge, why, and which view the editor adopts]

### Devil's Advocate Highlights
| Issue ID | Severity | Issue | Raised by Others? | Ruling | Resolvable by |
|----------|----------|-------|-------------------|--------|---------------|
| DA-C1 | CRITICAL | [issue] | [Yes/No; which reviewer] | [Upheld / Downgraded to MAJOR: reason] | [Clarification/minor additions / New data/experiments] |
| DA-M1 | MAJOR | [issue] | [Yes/No] | n/a | n/a |

---

## Revision Roadmap

### Priority 1 — Required (Must Fix)
*All Priority 1 items must be addressed for acceptance.*

| # | Issue | Source IDs | Location | Suggested Fix | Effort | Rebuttal-feasible? |
|---|-------|-----------|----------|---------------|--------|--------------------|
| R1 | [issue] | [e.g., DA-C1, R1-W2] | [Section/Table/Fig] | [fix] | [Low/Med/High; GPU-h] | [Yes/No] |
| R2 | [issue] | [IDs] | [location] | [fix] | [effort] | [Yes/No] |

### Priority 2 — Strongly Suggested (Should Fix)
*Addressing these significantly strengthens the paper.*

| # | Issue | Source IDs | Suggested Fix | Effort | Rebuttal-feasible? |
|---|-------|-----------|---------------|--------|--------------------|
| S1 | [issue] | [IDs] | [fix] | [effort] | [Yes/No] |

### Priority 3 — Nice to Fix (Optional)
*Would improve the paper but not required for acceptance.*

| # | Issue | Source | Suggestion |
|---|-------|--------|-----------|
| N1 | [issue] | [reviewer] | [suggestion] |

---

## Estimated Revision Effort
- Priority 1: [X items, estimated Y hours/days]
- Priority 2: [X items, estimated Y hours/days]
- Priority 3: [X items]
- **Total estimated revision time**: [estimate]
```

---

## Re-Review Decision Template

```markdown
# Verification Review Report

## Paper: [Full title]
## Review Type: Re-Review (Revision Verification)
## Date: [YYYY-MM-DD]
## Original Review Date: [date]

---

## Decision: [Accept / Minor Revision / Major Revision / Reject]

---

## Revision Response Checklist

### Priority 1 — Required Revisions

| # | Original Comment | Status | Location | Quality Assessment |
|---|-----------------|--------|----------|-------------------|
| R1 | [Original text] | [FULLY_ADDRESSED / PARTIALLY_ADDRESSED / NOT_ADDRESSED / MADE_WORSE] | [Section X.X] | [Assessment detail] |
| R2 | [Original text] | [Status] | [Location] | [Assessment] |

### Priority 2 — Suggested Revisions

| # | Original Comment | Status | Notes |
|---|-----------------|--------|-------|
| S1 | [Original text] | [Status] | [Notes or author explanation] |

### Priority 3 — Nice to Fix

| # | Original Comment | Status |
|---|-----------------|--------|
| N1 | [Original text] | [Status] |

---

## Response Letter Verification
| Claim in response letter | Found in manuscript? | Location | Note |
|--------------------------|---------------------|----------|------|
| [e.g., "Added a matched-backbone comparison"] | [Yes / No / Partially] | [Table X] | [..] |

---

## New Issues Discovered During Revision

| # | Type | Location | Description | Severity |
|---|------|----------|-------------|----------|
| NEW-1 | [Inconsistency/Error/Gap] | [Section X.X] | [Description] | [CRITICAL/MAJOR/MINOR] |

---

## Decision Rationale

[2–3 paragraphs explaining the decision based on the checklist above. Reference specific items.]

---

## Residual Issues (if any)

[List any unresolved items. Suggest which could be marked as Acknowledged Limitations vs. which truly need further revision.]

---

## Summary Statistics

| Category | Total | Fully Addressed | Partially | Not Addressed | Made Worse |
|----------|-------|----------------|-----------|---------------|------------|
| Priority 1 | [n] | [n] | [n] | [n] | [n] |
| Priority 2 | [n] | [n] | [n] | [n] | [n] |
| Priority 3 | [n] | [n] | [n] | [n] | [n] |
| New Issues | [n] | — | — | — | — |
```

---

## Response Letter (for Authors)

Authors' response letters use `templates/revision_response_template.md` (journals) or `templates/rebuttal_template.md` (conference rebuttals).
