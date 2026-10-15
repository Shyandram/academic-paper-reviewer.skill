# Peer Review Report Template

Use this template for all reviewers **except** the Devil's Advocate (who has a dedicated format in `agents/devils_advocate_reviewer_agent.md`).

---

```markdown
# Peer Review Report

## Paper: [Full paper title]
## Reviewer: [Name], [Role] ([descriptive affiliation]; fictional persona)
## Expertise: [2–3 specific areas]
## Date: [YYYY-MM-DD]

---

## Summary
[3–5 sentences summarizing the paper and its contributions IN YOUR OWN WORDS. This is not a place for criticism — the authors should generally agree with this summary. Do NOT copy the abstract.]

---

## Strengths

### S1: [Title of Strength]
[2–4 sentences. Be specific — cite sections, figures, or results.]

### S2: [Title of Strength]
[2–4 sentences.]

### S3: [Title of Strength]
[2–4 sentences.]

[Add more if warranted. Minimum 3 strengths.]

---

## Weaknesses

### W1: [Title of Weakness]
[2–4 sentences describing the issue. Cite specific locations (Section X.X, Table Y, Figure Z, Equation N).]
- **Suggested Fix**: [Concrete, actionable suggestion for improvement.]

### W2: [Title of Weakness]
[2–4 sentences.]
- **Suggested Fix**: [Suggestion.]

[Add more if warranted. Minimum 2 weaknesses. Every weakness MUST have a suggested fix. Order by severity, most severe first.]

---

## Missing References (Domain Reviewer: required; others: optional)

*Follow the citation-integrity rule: only references you are confident exist; otherwise describe the line of work or mark `[verify]`.*

| Priority | Reference (authors, title, venue/year) | Why it matters |
|----------|----------------------------------------|----------------|
| Critical | | |
| Important | | |
| Helpful | | |

---

## NeurIPS-Style Scores

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| Quality | [1–4] | [1 sentence] |
| Clarity | [1–4] | [1 sentence] |
| Significance | [1–4] | [1 sentence] |
| Originality | [1–4] | [1 sentence] |

**Score Key**: 4 = Excellent, 3 = Good, 2 = Fair, 1 = Poor

---

## Dimension Scores (0–100)

*Use the calibrated rubrics in `references/quality_rubrics.md`. For each dimension, select the descriptor that best matches and assign a score within that band.*

| Dimension | Score | Descriptor | Rationale |
|-----------|-------|------------|-----------|
| Technical Rigor | [0–100] | [Exceptional/Strong/Competent/Developing/Inadequate] | [Brief justification] |
| Clarity & Presentation | [0–100] | [descriptor] | [Brief justification] |
| Novelty & Originality | [0–100] | [descriptor] | [Brief justification] |
| Significance & Impact | [0–100] | [descriptor] | [Brief justification] |
| Experimental Validation | [0–100] | [descriptor] | [Brief justification] |
| Reproducibility | [0–100] | [descriptor] | [Brief justification] |
| Ethical Compliance | [0–100] | [descriptor] | [Brief justification] |

---

## Questions for Authors

*3–5 key questions. Focus on points where an author response could change your assessment. State clearly what would raise or lower your score.*

1. [Question — include what answer would raise/lower your score]
2. [Question]
3. [Question]

---

## Limitations Assessment

**Have the authors adequately addressed limitations?**
[Yes / Partially / No]

[If not "Yes": Constructive suggestions for what to add. Remember — authors should be rewarded for honesty about limitations, not punished.]

---

## Ethics Review Flag

**[No / Yes]**: [If Yes: the specific concern (e.g., consent for face data, misuse potential, data licensing) and why it needs ethics review]

---

## Overall Score

**[1–6]**: [1–2 sentence justification]

**Overall Score Key**:
- 6: Strong Accept — Technically flawless, groundbreaking impact
- 5: Accept — Technically solid, high impact
- 4: Borderline Accept — Solid, reasons to accept outweigh reject
- 3: Borderline Reject — Solid, reasons to reject outweigh accept
- 2: Reject — Technical flaws, weak evaluation
- 1: Strong Reject — Well-known results or unaddressed ethics

## Confidence

**[1–5]**: [Brief explanation]

**Confidence Key**:
- 5: Absolutely certain, very familiar with related work, checked details carefully
- 4: Confident but not absolutely certain
- 3: Fairly confident, may have missed some parts
- 2: Willing to defend but may have misunderstood central parts
- 1: Best guess
```

---

## Template Usage Notes

- **Strengths and Weaknesses must be balanced.** A review with only weaknesses is unhelpful; a review with only strengths is not a review.
- **Specificity matters.** "The writing is unclear" is useless. "Section 3.2 introduces notation $\mathcal{L}_{total}$ without defining the individual loss terms" is useful.
- **Suggested Fixes are mandatory.** Every weakness must include at least one concrete suggestion. "Do better" is not a suggestion.
- **Scores must be consistent with text.** If you list serious weaknesses, don't give a score of 4/4 on Quality. If you praise the writing, don't give Clarity 1/4.
- **Questions should be strategic.** Ask things where the answer would genuinely change your assessment.
- **Use the 0–100 → 1–4 mapping** in `references/quality_rubrics.md` so the two score sets agree.
- **No fabricated content.** Every cited location must exist in the manuscript; every recommended reference must follow the citation-integrity rule.
