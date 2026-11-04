# Editorial Decision Template

## Full Review Decision

```markdown
# Editorial Decision

## Paper: [Full title]
## Submission ID: [if available]
## Date: [YYYY-MM-DD]
## Target Venue: [venue] | Paper Type: [type]
## Review Team (fictional personas): EIC (meta-reviewer) [name]; R1 Methodology, R2 Domain, R3 Perspective, R4 Generalist, DA [names]

---

## Decision: [Strong Accept (6) / Accept (5) / Borderline Accept (4) / Borderline Reject (3) / Reject (2) / Strong Reject (1)]

**BEFORE** (confidence-weighted): [composite] → [band] | **AFTER** (EIC-weighted): [composite] → [band] | **DA ceiling**: [none / 4 / 3] | **Final (EIC)**: [n]
**Journal recommendation** (if journal target): [Accept / Minor Revision / Major Revision / Reject]

---

## EIC Meta-Review

### The Case For and Against
- **For acceptance:** [2–3 sentences]
- **Against acceptance:** [2–3 sentences]

### Verification of Decisive Points (EIC read of the paper)
| Point | Raised by | Location | EIC finding | Note |
|-------|-----------|----------|-------------|------|
| [e.g., headline gain vs. best prior] | [DA-C1, R1-W1] | [Table 2] | [Verified / Partly correct / Overstated / Incorrect] | [..] |

### Reviewer Weights
| Reviewer | Overall | Confidence | EIC quality weight (0.5–1.5) | Reason |
|----------|---------|------------|------------------------------|--------|
| R1 (Methodology) | | | | [one line] |
| R2 (Domain) | | | | |
| R3 (Perspective) | | | | |
| R4 (Generalist) | | | | |
| DA | | | | |

### DA-CRITICAL Rulings
| Issue | AC test: fatal on its own? | Ruling | Resolvable by |
|-------|---------------------------|--------|---------------|
| DA-C1 | [Yes / No: why] | [Upheld / Downgraded to MAJOR] | [Clarification/minor additions / New data/experiments] |

### Final Decision and Justification
[One paragraph. If the decision differs from the AFTER band, explain why, e.g., "a novel contribution whose weaknesses are typical of accepted papers at this venue". Confirm it does not exceed the DA ceiling.]

---

## Score Summary

### BEFORE and AFTER Scores

*Paste the markdown output of `python3 scripts/aggregate_scores.py scores.json --venue <target>` (run with the EIC's `eic_weight` values): the reviewer-weight table and the BEFORE/AFTER dimension table. Or fill them in by hand with the same formulas.*

| Dimension | R1 | R2 | R3 | R4 | DA | Before (confidence) | After (EIC-weighted) | Spread |
|-----------|----|----|----|----|----|---------------------|----------------------|--------|
| Technical Rigor | | | | | | | | |
| Clarity & Presentation | | | | | | | | |
| Novelty & Originality | | | | | | | | |
| Significance & Impact | | | | | | | | |
| Experimental Validation | | | | | | | | |
| Reproducibility | | | | | | | | |
| Ethical Compliance | | | | | | | | |
| **Composite** | | | | | | **[before]** | **[after]** | |

### Target-Venue Scores ([venue], scale status: [official / confirmed / secondary / assumed / unpublished])

| Venue field | Score |
|-------------|-------|
| [e.g., Soundness / Presentation / Contribution, or Claims & evidence / Audience] | [..] |
| [Venue overall rating / recommendation] | [..] |

### Cross-Venue Outlook (if requested)

[Paste the `--all-venues` table from `scripts/aggregate_scores.py`, then 2–4 sentences of content-based venue advice. Heuristic, not a prediction.]

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
Editor-in-Chief (meta-reviewer)

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
