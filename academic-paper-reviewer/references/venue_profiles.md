# Venue Profiles

Review-form conventions and rebuttal formats for common CV/ML venues. **Venues revise their forms, scales, page limits and policies almost every year.** Use this file for orientation, check the current call for papers or author guidelines whenever specifics matter, and tell the user to do the same.

The skill always scores internally on its own scales (NeurIPS-style 1–4, Overall 1–6, Confidence 1–5, and the 0–100 dimensions). When a venue uses a different scale, translate with the tables below and show both.

---

## Conferences

| Venue | Review style (typical) | Rebuttal (typical) | Notes |
|-------|------------------------|--------------------|-------|
| **CVPR / ICCV / ECCV** | Summary, strengths, weaknesses, a justification for the rating, and an overall recommendation on a short ordinal scale (the labels change between years) | One-page PDF in the venue's template. New experiments are often limited by the rules; check them. | Double-blind with strict anonymity (no identifying links or acknowledgments). Supplementary material allowed. |
| **NeurIPS** | Summary, strengths & weaknesses, questions, limitations, ethics flag; sub-scores on 1–4 scales; Overall on a 1–6 scale in recent editions; Confidence 1–5 | OpenReview comments with character limits, then a discussion period | Paper checklist required. Answering "no" to a checklist question is not by itself grounds for rejection. |
| **ICLR** | Soundness / Presentation / Contribution (1–4), Rating on {1, 3, 5, 6, 8, 10}, Confidence 1–5 | Open discussion on OpenReview; revised PDFs can be uploaded during discussion | Reviews and submissions are public. |
| **ICML** | Similar structure to NeurIPS; an overall recommendation on a short ordinal scale | OpenReview author response | |
| **AAAI / IJCAI** | Structured form with an overall score | Short author response | |
| **BMVC / WACV / ACCV** | Lighter forms; WACV has algorithms and applications tracks | Varies | Good fits for solid but narrower contributions |
| **MICCAI** (medical imaging) | Form with clinical-relevance emphasis | Short rebuttal | Reproducibility checklist |
| **Workshops** | Short form | Usually none | Work in progress acceptable |

### Scale Translation (internal Overall 1–6 → venue)

| Internal Overall | ICLR rating | Short ordinal CV scales (generic) |
|------------------|-------------|-------------------------------|
| 6 Strong Accept | 10 (or 8) | Strong accept / Accept |
| 5 Accept | 8 | Accept / Weak accept |
| 4 Borderline Accept | 6 | Borderline accept / Weak accept |
| 3 Borderline Reject | 5 | Borderline reject / Weak reject |
| 2 Reject | 3 | Reject / Weak reject |
| 1 Strong Reject | 1 | Strong reject |

---

## Journals

| Venue | Recommendation options (typical) | Notes |
|-------|----------------------------------|-------|
| **TPAMI / IJCV / TIP / TMLR / Pattern Recognition** | Accept · Minor Revision · Major Revision · Reject (sometimes "Reject & Resubmit") | Extended conference versions usually need substantial new content (often expected to be about 30% or more; check the policy). TMLR emphasizes correctness and clarity of claims over novelty. |
| **Nature-family / Science-family** | Accept · Revise · Reject; strong emphasis on broad significance | Editor triage before review; a cover letter and broad-audience framing matter. |

Use the Conference ↔ Journal Mapping in `references/editorial_decision_standards.md`.

---

## Policies That Commonly Affect Reviews

- **Anonymity**: double-blind at most CV/ML conferences. Flag identifying links, acknowledgments, self-citations in the first person ("our previous work [12]"), and non-anonymized code repositories.
- **Concurrent work**: venues usually exempt papers published shortly before the deadline (often within roughly two months) from required comparison. Don't penalize missing comparisons with very recent arXiv preprints.
- **arXiv preprints**: generally allowed; reviewers should not search for the authors.
- **LLM use**: many venues restrict putting confidential submissions into AI tools and require authors to disclose substantive LLM use. See *Responsible Use* in `SKILL.md`.
- **Page limits**: main paper limits typically exclude references; appendices and supplementary material may or may not count. Check the venue.
- **Reproducibility / ethics checklists**: NeurIPS-style checklists and ethics statements are required at several venues. Missing ones can lead to desk rejection.
