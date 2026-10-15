# Venue Profiles

How each supported venue reviews papers, and how the skill's internal scores are translated into each venue's own form. The machine-readable version is `scripts/venues.json`, used by `scripts/aggregate_scores.py --venue <key>` and `--all-venues`.

**Venues revise their forms, scales and policies almost every year.** Every profile records the cycle it describes and a **verification status**:

| Status | Meaning | How to present it |
|--------|---------|-------------------|
| `official` | Taken from the venue's own guidelines | State it as the venue's scale |
| `secondary` | Several consistent but non-official sources (published analyses, community reports) | "Recent forms use…; verify against the current form" |
| `assumed` | Not found; mapped from a sibling venue | "Assumed (CVF-style); check the current form" |
| `unpublished` | The venue does not publish its scale | Show a generic recommendation only |

Never present a `secondary`, `assumed` or `unpublished` label as the venue's official wording.

---

## How Translation Works

1. Reviewers score on the internal scales (NeurIPS-style 1–4, Overall 1–6, Confidence 1–5, and the seven 0–100 dimensions), **anchored to the target venue's bar**.
2. For each venue, the paper-type weights are multiplied by that venue's **emphasis** vector and renormalized, giving a **venue-weighted composite**. Emphasis vectors are the skill's heuristics, derived from each venue's stated criteria, not official weights.
3. A **bar offset** shifts the band thresholds: positive is harder (TPAMI +3), negative is more lenient on these dimensions (TMLR −5, TIP −2).
4. Upheld DA-CRITICAL caps apply at **every** venue.
5. The band is mapped to the venue's own scale and sub-scores (e.g., ICLR Soundness/Presentation/Contribution, NeurIPS Quality/Clarity/Significance/Originality, the TMLR Yes/No criteria).

Emphasis order: Technical Rigor, Clarity, Novelty, Significance, Experimental Validation, Reproducibility, Ethics.

| Key | Venue | Kind | Cycle | Emphasis | Bar | Scale status |
|-----|-------|------|-------|----------|-----|--------------|
| `cvpr` | CVPR | Conf. | 2026 | 1.0 / 1.0 / 1.1 / 1.0 / **1.3** / 1.0 / 0.8 | +0 | secondary |
| `iccv` | ICCV | Conf. | 2025 | 1.0 / 1.0 / 1.1 / 1.0 / **1.3** / 1.0 / 0.8 | +0 | secondary |
| `eccv` | ECCV | Conf. | 2026 | 1.0 / 1.0 / **1.2** / 1.1 / 1.1 / 1.0 / 0.8 | +0 | assumed |
| `neurips` | NeurIPS | Conf. | 2025 | 1.1 / 1.0 / 1.1 / 1.1 / 1.0 / 1.0 / 1.0 | +0 | secondary |
| `iclr` | ICLR | Conf. | 2026 | **1.2** / 1.1 / 1.1 / 1.1 / 1.0 / 1.0 / 0.8 | +0 | secondary |
| `icml` | ICML | Conf. | 2025 | **1.3** / 1.0 / 1.0 / 1.0 / 1.1 / 1.0 / 0.8 | +0 | official |
| `aaai` | AAAI | Conf. | 2026 | 1.1 / 1.0 / 1.1 / 1.1 / 1.0 / 0.9 / 0.9 | +0 | unpublished |
| `acmmm` | ACM Multimedia | Conf. | 2026 | 1.0 / 1.0 / **1.2** / **1.2** / 1.0 / 1.1 / 0.9 | +0 | unpublished |
| `tmlr` | TMLR | Journal | 2025 | **1.5 / 1.3** / 0.4 / 0.5 / **1.3** / 1.1 / 1.0 | −5 | official |
| `tpami` | IEEE TPAMI | Journal | 2025 | **1.3** / 1.1 / 1.0 / 1.1 / **1.3** / 1.1 / 0.9 | +3 | secondary |
| `tip` | IEEE TIP | Journal | 2025 | 1.2 / 1.1 / 1.0 / 1.0 / **1.3** / 1.1 / 0.8 | −2 | assumed |

---

## Computer Vision Conferences (CVF / ECVA)

### CVPR (`cvpr`, 2026 cycle; scale status: secondary)
- **Form:** summary, strengths, weaknesses, a preliminary rating, then a final rating with a justification after the rebuttal and discussion. Recent training material uses labels including *Weak Accept* and *Borderline*, and requires the final justification to be specific, evidence-based and **explicitly tied to the rating**, including an explanation of any change after the rebuttal.
- **Scale used by the skill (assumed CVF-style):** 6 Accept · 5 Weak Accept · 4 Borderline Accept · 3 Borderline Reject · 2 Weak Reject · 1 Reject.
- **Emphasis:** technical novelty plus strong, controlled experiments on standard benchmarks; ablations; visual evidence.
- **Rebuttal:** one-page PDF in the CVPR template.
- **Decision:** ACs, SACs and PCs decide from the reviewers' input.

### ICCV (`iccv`, 2025 cycle; secondary)
- **Scale (community reports for 2025):** 6 Accept, 5 Weak Accept, 4 Borderline Accept. Labels 3–1 inferred as Borderline Reject / Weak Reject / Reject.
- **Policy:** reviews flagged as highly irresponsible (one sentence long, LLM-generated, irrelevant, or ignoring large parts of the paper) and missed review deadlines can lead to desk rejection of the reviewer's own papers.
- **Rebuttal:** one-page PDF.

### ECCV (`eccv`, 2026 cycle; scale assumed)
- **Contribution Types:** authors declare a contribution type, and reviewers and ACs judge the paper against type-specific criteria. The Field Analyst records the declared type (see `agents/field_analyst_agent.md`).
- **Guidance:** look for what is good or stimulating and what knowledge it advances. **Not exceeding SOTA on an existing benchmark is not by itself grounds for rejection.** Failing to cite or beat an arXiv paper must not be the *sole* reason to reject.
- **LLM policy:** LLMs may not be used to write reviews or meta-reviews (locally or via an API). Background research and grammar checks on short phrases are allowed.
- **Scale:** not confirmed; the CVF-style 6-point scale is assumed.
- **Rebuttal:** one-page PDF; strict deadlines.

## Machine Learning Conferences

### NeurIPS (`neurips`, 2025 cycle; secondary)
- **Form:** Summary; Strengths and Weaknesses; **Quality, Clarity, Significance, Originality (1–4)**; Questions; Limitations; **Overall (1–6)**; **Confidence (1–5)**; Ethical concerns.
- The skill's internal scales follow this form, so translation is direct: 6 Strong Accept … 4 Borderline accept · 3 Borderline reject … 1 Strong Reject.
- **Guidance:** originality need not mean an entirely new method. Reward honest limitations. The paper checklist is a tool, and a "no" answer is not by itself grounds for rejection.
- **Rebuttal:** OpenReview comments with character limits, then a discussion period.

### ICLR (`iclr`, 2026 cycle; secondary)
- **Form:** Summary; **Soundness, Presentation, Contribution (1–4)**; Strengths; Weaknesses; Questions; **Rating**; **Confidence (1–5)**.
- **Rating:** recent analyses report {0, 2, 4, 6, 8, 10} for ICLR 2026; earlier cycles used {1, 3, 5, 6, 8, 10} with 6 as the acceptance threshold. The script prints both.
- **Sub-score derivation:** Soundness ← mean(Technical Rigor, Experimental Validation); Presentation ← Clarity; Contribution ← mean(Novelty, Significance); each mapped with the 0–100 → 1–4 table.
- **Process:** submissions and reviews are public. Authors can upload a revised PDF during the discussion, so separate fixable issues from fundamental ones.

### ICML (`icml`, 2025 cycle; official)
- **Form (2025):** Summary; **Claims and Evidence**; Relation to Prior Works; Other Aspects (originality, significance, clarity); Questions for Authors; Ethical Issues; **Overall Recommendation (1–5)**.
- **Scale (2025):** 5 Strong accept · 4 Accept · 3 Weak accept (leaning accept, could be rejected) · 2 Weak reject (leaning reject, could be accepted) · 1 Reject.
- **2026 note:** reportedly a 6-point scale (Weak Accept = 4, Weak Reject = 3, upper labels "use sparingly"). When targeting 2026, report the internal 1–6 score with those labels and mark it secondary.
- **Emphasis:** claims must be backed by evidence, and every strength or weakness must be substantiated.

### AAAI (`aaai`, AAAI-26; unpublished scale)
- **Process:** two phases. In Phase 1, three reviewers. Papers with sufficiently negative Phase-1 reviews can be rejected **before** author feedback. Survivors get more reviewers in Phase 2.
- **Criteria (reported):** clarity, technical and experimental soundness, novelty, relevance. The numeric scale is not published, so the skill gives a generic recommendation and a **Phase-1 risk flag** (moderate at band 3, high at ≤ 2).
- **AAAI-26 pilot:** every main-track paper also received one clearly labeled AI review, which carries no rating.

### ACM Multimedia (`acmmm`, 2026 guidelines; unpublished scale)
- **Criteria:** novelty, scientific rigor, claims supported by evidence, code/data release. **Scope gate:** papers on a narrow single modality that don't contribute to the human use of multimedia may be rejected as out of scope. Separate minor camera-ready fixes from major flaws.
- **Rebuttal:** optional, on OpenReview; must stay anonymous and **cannot link to external material** (code, videos).
- **Skill behavior:** the EIC explicitly assesses multimedia relevance; the generic recommendation scale is used.

## Journals

### TMLR (`tmlr`; official)
- **Two acceptance criteria, each answered Yes/No with an explanation:**
  1. *Are the claims made in the submission supported by accurate, convincing and clear evidence?* This is the most important criterion. Over-claiming is fixed by adding evidence **or by narrowing the claims**.
  2. *Would some individuals in TMLR's audience be interested in the findings?* If unsure, the reviewer should assume yes.
- Papers meeting both criteria are accepted **even if the contribution is modest**. Lack of SOTA results or perceived lack of novelty is not grounds for rejection.
- **Script mapping:** Claims ← mean(Technical Rigor, Experimental Validation, Clarity) ≥ 60 and no upheld unresolvable DA-CRITICAL issue; Audience ← mean(Novelty, Significance) ≥ 40. Outcome: Accept / Accept with minor revision / Reject (or major changes).
- **Report format:** summary of contributions; strengths and weaknesses; *requested changes*, split into critical vs. strengthening; the two criteria.

### IEEE TPAMI (`tpami`; secondary)
- **Recommendation options (IEEE Computer Society):** Accept · Minor Revision · Major Revision · Revise and Resubmit · Reject. A second major revision is generally not granted, so a Major Revision must list *everything* needed.
- **Bar (+3):** a top-conference bar plus completeness, depth and comprehensive comparisons. Extended conference versions need substantial new content beyond the authors' own conference paper.
- **Report format:** comments to authors, plus confidential comments to the editor.

### IEEE TIP (`tip`; assumed)
- **Scope:** image processing (restoration, compression, enhancement, analysis); its applications to vision are in scope when the image-processing contribution is central.
- **Recommendation menu:** not confirmed; IEEE-style options assumed (Accept / Minor Revision / Major Revision / Reject & Resubmit / Reject).
- **Emphasis:** fair baselines and ablations that separate the contribution from architecture size, data, supervision and tuning; reproducibility.

---

## Common Policies

- **Anonymity:** double-blind at all conferences above. Flag identifying links, acknowledgments, first-person self-citations and non-anonymized repositories.
- **Concurrent work:** don't penalize missing comparisons with very recent arXiv preprints (see the ECCV guidance above; most venues have similar rules).
- **LLM use:** CVF and ECCV reviewers may not use LLMs to write reviews, and ICCV penalizes LLM-generated reviews. Most venues restrict uploading confidential submissions to AI tools. See *Responsible Use* in `SKILL.md`.

## Sources (accessed 2026-10)

The official pages could not be fetched directly when this file was written; details marked *secondary* come from search summaries of them and from published analyses. Re-verify before each cycle.

- CVPR 2026 Reviewer Guidelines and Reviewer Training Material: cvpr.thecvf.com/Conferences/2026/ReviewerGuidelines, …/ReviewerTrainingMaterial
- ICCV 2025 Reviewer Guidelines and Changes: iccv.thecvf.com/Conferences/2025/ReviewerGuidelines, …/Changes
- ECCV 2026 Reviewer Guide: eccv.ecva.net/Conferences/2026/ReviewerGuide
- NeurIPS 2025/2026 Reviewer Guidelines: neurips.cc/Conferences/2025/ReviewerGuidelines
- ICLR 2026 Reviewer Guide: iclr.cc/Conferences/2026/ReviewerGuide
- ICML 2025/2026 Reviewer Instructions: icml.cc/Conferences/2025/ReviewerInstructions, …/2026/ReviewerInstructions
- AAAI-26 Review Process: aaai.org/conference/aaai/aaai-26/review-process/; AAAI-26 AI Review Pilot (arXiv 2604.13940)
- ACM MM 2026 Reviewer and AC Guidelines: 2026.acmmm.org/site/review-process-guidelines.html; ACM MM 2025 Call for Papers: acmmm2025.org/call-for-papers/
- TMLR Reviewer Guide and Acceptance Criteria: jmlr.org/tmlr/reviewer-guide.html, jmlr.org/tmlr/acceptance-criteria.html
- IEEE Computer Society, Making Peer Review Recommendations: computer.org/publications/making-peer-review-recommendations
