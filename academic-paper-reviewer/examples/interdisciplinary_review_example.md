# Example: Interdisciplinary Review (Medical Imaging × Clinical Practice)

> **Illustrative example.** The paper, reviewers, numbers and findings are entirely fictional. They show how the panel is configured for a paper that spans ML and a clinical domain, and a case where the EIC **upholds** a DA-CRITICAL issue. Compare `cv_paper_review_example.md`, where one is downgraded. Abbreviated.

**Fictional paper**: *"Foundation-Model Features for Early Detection of Diabetic Retinopathy from Smartphone Fundus Images"*. Target venue: a medical-imaging conference (stated by the user).

---

## Phase 0: Reviewer Configuration Card

| Item | Finding |
|------|---------|
| Primary Discipline | Medical Image Analysis → Retinal Imaging |
| Secondary Discipline(s) | Self-supervised representation learning; ophthalmology; global health |
| Paper Type | Empirical (composite weights: empirical) |
| Core Technique(s) | Frozen vision foundation-model features + linear/MLP heads |
| Target Venue | Medical-imaging conference (stated) |
| Paper Maturity | Submission-ready |
| Ethics-Relevant Content | Patient images; low-resource deployment setting |

**Team (fictional personas)**
- **EIC (meta-reviewer)**: Prof. Camila Ferreira-Lund, medical-imaging group, university hospital (Europe). Retinal imaging, clinical translation.
- **R1 (Methodology)**: Dr. Kwame Asante, biostatistics unit, school of public health (West Africa). Diagnostic-accuracy studies, external validation.
- **R2 (Domain)**: Dr. Mei Takahara, ophthalmic imaging lab (East Asia). Fundus image analysis, DR grading.
- **R3 (Perspective)**: Dr. Lucía Paredes, global-health program (South America). Screening programs in low-resource settings.
- **R4 (Generalist)**: Dr. Hana Kovář, medical image computing group, technical university (Central Europe). Broad medical-imaging background.
- **Devil's Advocate**: Dr. Erik Solberg, ML-robustness group, research institute (Northern Europe). Shortcut learning, dataset shift.

---

## Phase 1: Key Findings (abbreviated)

- **R1 (Overall 3)**: splits appear to be at the *image* level (§4.1). Several patients contribute both eyes and repeat visits, a leakage risk. AUC is reported without CIs, and sensitivity at a clinically relevant specificity is missing. External validation is on one additional site captured with the *same* phone model.
- **R2 (Overall 4)**: positioning omits prior smartphone-fundus screening studies. The grading protocol (number and type of graders, adjudication) is under-specified.
- **R3 (Overall 4)**: a strong case for low-resource screening. Cost per screen, offline inference and the referral pathway are not discussed. Suggests testing image-quality gating, since many real captures are ungradable.
- **R4 Generalist (Overall 4)**: clinically important and well motivated; the smartphone setting is novel for this venue. The intended clinical workflow (screening vs. referral) is unclear.
- **Devil's Advocate (Overall 2)**
  - *Strongest counter-argument*: the frozen features may detect *capture conditions* (clinic vs. field, phone model, illumination) correlated with disease prevalence in the collected data, not retinopathy itself. Positive cases come mostly from the tertiary clinic site (Table 1), so site is confounded with label.
  - **DA-C1 (CRITICAL; needs new data/experiments)**: confounded site and label, plus image-level splits. The reported AUC may reflect shortcut learning and leakage.
  - **DA-M1 (MAJOR)**: no subgroup analysis (age, sex, skin and fundus pigmentation) despite the global-health framing.

## Phase 2: EIC Meta-Review and Decision

| Consensus map | Sources | Class |
|---------------|---------|-------|
| Leakage / confounded evaluation | R1, DA | CONSENSUS-2 + DA-CRITICAL |
| Clinical workflow & metrics underspecified | R4, R1, R3 | CONSENSUS-3 |
| Grading protocol unclear | R2, R1 | CONSENSUS-2 |
| Subgroup / fairness analysis missing | DA, R3 | CONSENSUS-2 |
| Low-resource relevance is a real strength | R4, R3 | CONSENSUS-2 (positive) |

**EIC verification**: Table 1 confirms that 81% of positive cases come from the tertiary clinic site, and §4.1 confirms that splits are at the image level, with repeat visits per patient. *Verified.*

**DA-CRITICAL ruling**: **upheld.** AC test: yes, fatal on its own. With site confounded with label and patient-level leakage, the experiment **cannot test** whether the model detects retinopathy. This meets the strict criteria ("cannot test the claim", "evaluation leakage"). It is not a confound that one more baseline could resolve. Needs new experiments → ceiling 3.

**Reviewer weights**: R1 1.25 (verified leakage, decisive) · DA 1.25 (verified, correctly scoped) · R2 1.0 · R4 1.0 · R3 1.0.

**BEFORE** 59.4 → 3 · **AFTER** 58.7 → 3 · **DA ceiling**: 3 · **Final (EIC): 3, Borderline Reject** (journal equivalent: Major Revision). Strengths are real, but no score can override an upheld fatal flaw in the evaluation.

**Priority 1 roadmap**
| # | Issue | Fix | Effort |
|---|-------|-----|--------|
| R1 | Patient-level splits; re-evaluate | Re-split by patient; rerun all experiments | Medium |
| R2 | Site–label confound (DA-C1) | Site-stratified analysis; train on one site and test on another; report AUC within site | High |
| R3 | Clinical metrics | Sensitivity at 80/90% specificity with 95% bootstrap CIs; define the workflow | Low |
| R4 | External validation on a different phone model or capture protocol | Add a site with a different device, or state the limitation explicitly | High |

*Key lesson*: the cross-disciplinary reviewer (R3) and the DA reach the same concern from different directions (deployment realism vs. shortcut learning). The synthesizer merges them without double-counting, and the EIC checks the shared concern against Table 1 before deciding.
