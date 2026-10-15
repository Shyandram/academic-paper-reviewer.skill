# Example: Interdisciplinary Review (Medical Imaging × Clinical Practice)

> **Illustrative example.** The paper, reviewers, numbers and findings are entirely fictional. They show how the panel is configured and how the decision is reached for a paper that spans ML and a clinical domain. Abbreviated.

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

**Review team (fictional personas)**
- **EIC**: Prof. Camila Ferreira-Lund, medical-imaging group, university hospital (Europe). Retinal imaging, clinical translation.
- **R1 (Methodology)**: Dr. Kwame Asante, biostatistics unit, school of public health (West Africa). Diagnostic-accuracy studies, external validation.
- **R2 (Domain)**: Dr. Mei Takahara, ophthalmic imaging lab (East Asia). Fundus image analysis, DR grading.
- **R3 (Perspective)**: Dr. Lucía Paredes, global-health program (South America). Screening programs in low-resource settings.
- **Devil's Advocate**: Dr. Erik Solberg, ML-robustness group, research institute (Northern Europe). Shortcut learning, dataset shift.

---

## Phase 1: Key Findings (abbreviated)

- **EIC (Overall 4)**: clinically important and well motivated; the smartphone setting is novel for this venue. The paper is unclear about the intended clinical workflow (screening vs. referral).
- **R1 (Overall 3)**: splits appear to be at the *image* level (§4.1). Several patients contribute both eyes and repeat visits, a leakage risk. AUC is reported without CIs, and sensitivity at a clinically relevant specificity is missing. External validation is on one additional site captured with the *same* phone model.
- **R2 (Overall 4)**: positioning omits prior smartphone-fundus screening studies. The grading protocol (number and type of graders, adjudication) is under-specified.
- **R3 (Overall 4)**: a strong case for low-resource screening. Cost per screen, offline inference and the referral pathway are not discussed. Suggests testing image-quality gating, since many real captures are ungradable.
- **Devil's Advocate (Overall 2)**
  - *Strongest counter-argument*: the frozen features may detect *capture conditions* (clinic vs. field, phone model, illumination) correlated with disease prevalence in the collected data, not retinopathy itself. Positive cases come mostly from the tertiary clinic site (Table 1), so site is confounded with label.
  - **DA-C1 (CRITICAL; needs new data/experiments)**: confounded site and label, plus image-level splits. The reported AUC may reflect shortcut learning and leakage.
  - **DA-M1 (MAJOR)**: no subgroup analysis (age, sex, skin and fundus pigmentation) despite the global-health framing.

## Phase 2: Decision

| Consensus map | Sources | Class |
|---------------|---------|-------|
| Leakage / confounded evaluation | R1, DA | CONSENSUS-2 + DA-CRITICAL |
| Clinical workflow & metrics underspecified | EIC, R1, R3 | CONSENSUS-3 |
| Grading protocol unclear | R2, R1 | CONSENSUS-2 |
| Subgroup / fairness analysis missing | DA, R3 | CONSENSUS-2 |
| Low-resource relevance is a real strength | EIC, R3 | CONSENSUS-2 (positive) |

**Composite**: 58.7 → implied 3. **DA cap**: 3 (DA-C1 upheld; needs new experiments). **Decision: 3, Borderline Reject** (journal equivalent: Major Revision).

**Priority 1 roadmap**
| # | Issue | Fix | Effort |
|---|-------|-----|--------|
| R1 | Patient-level splits; re-evaluate | Re-split by patient; rerun all experiments | Medium |
| R2 | Site–label confound (DA-C1) | Site-stratified analysis; train on one site and test on another; report AUC within site | High |
| R3 | Clinical metrics | Sensitivity at 80/90% specificity with 95% bootstrap CIs; define the workflow | Low |
| R4 | External validation on a different phone model or capture protocol | Add a site with a different device, or state the limitation explicitly | High |

*Key lesson*: the cross-disciplinary reviewer (R3) and the DA reach the same concern from different directions (deployment realism vs. shortcut learning). The synthesizer merges them without double-counting.
