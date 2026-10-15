# Rebuttal Template (Conference)

For conferences with a short rebuttal phase. Two layouts are given: a **one-page PDF** (common at CVPR/ICCV/ECCV) and **per-reviewer OpenReview comments** (common at NeurIPS/ICLR/ICML). Check the current year's author guidelines for the exact limits and rules (page count, character limits, whether new results or figures are allowed, whether links are allowed).

---

## Layout A: One-Page PDF

```markdown
# Rebuttal: Paper ID [####]

We thank the reviewers for their constructive feedback and are encouraged that they found [strength 1] (R1, R3), [strength 2] (R2) and [strength 3] (R1, R2). We address the main concerns below; new results are in Tables A–B.

**[Shared concern 1, e.g., "Fairness of comparison" (R1, R2)]**
[Conclusion first. Evidence: new controlled result or exact location in the paper. Planned change for the camera-ready.]

| Method | Backbone | Pretrain | Res. | mIoU |
|--------|----------|----------|------|------|
| Baseline X (matched) | | | | [TBD] |
| Ours | | | | |
*Table A: [caption]*

**[Shared concern 2] (R2, R3)**
[...]

**R1: [specific point]**: [answer]
**R2: [specific point]**: [answer]
**R3: [specific point]**: [answer]

**Minor points.** [Typos, clarifications, missing references, answered together in 2–3 lines.] We will fix all of them in the final version.
```

Tips for the one-page format:
- Use compact `\paragraph{}` headers and small tables. Readers skim, so make the first sentence of each paragraph the answer.
- Reference reviewers as R1/R2/R3 exactly as the venue labels them.
- Don't use the space to restate the reviewers' points at length.

---

## Layout B: Per-Reviewer Comments (OpenReview)

```markdown
## General Response (to all reviewers)

We thank all reviewers. Common strengths noted: [..]. Main new evidence: [..]. Summary of changes we will make: [..].

---

## Response to Reviewer [ID]

We thank the reviewer for [specific appreciation].

**W1 / Q1: [short paraphrase]**
[Conclusion first.] [Evidence or new result.] [Change to the paper: section, what is added.]

**W2: [short paraphrase]**
[...]

**Q3: [short paraphrase]**
[...]

We hope these responses address the reviewer's concerns, and we would be glad to clarify anything further during the discussion period.
```

Tips for OpenReview:
- Stay within the per-comment character limit. If you need more room, put shared content in the general response and refer to it.
- Markdown and LaTeX render. Keep tables small.
- During the discussion period, reply promptly and briefly to follow-up questions.

---

## Pending-Results Ledger (keep for the authors; do not submit)

| Placeholder | What to fill | Experiment / source | Owner | Done |
|-------------|--------------|---------------------|-------|------|
| [TBD-1] | | | | ☐ |
