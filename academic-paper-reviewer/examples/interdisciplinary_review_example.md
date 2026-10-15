# Example: Full Review — "Using Machine Learning to Predict University Closure Risk in Taiwan"

This example demonstrates the review of an interdisciplinary paper spanning machine learning and higher education policy.

---

## Phase 0 Output: Reviewer Configuration Card

### Paper Analysis

| Item | Finding |
|------|---------|
| Primary Discipline | Machine Learning (Applied) |
| Secondary Discipline | Higher Education Policy, Institutional Economics |
| Research Paradigm | Empirical |
| Methodology Type | Predictive Modeling + Feature Analysis |
| Target Venue | Computers & Education / Expert Systems with Applications |
| Paper Maturity | Submission-ready |

### Review Team

- **EIC**: Prof. Rebecca Liu — National University of Singapore. Expertise: AI in Education, Educational Data Mining. Style: Expects both ML rigor and domain relevance.
- **R1 (Methodology)**: Prof. Dimitri Volkov — EPFL. Expertise: Gradient Boosting, Time Series Classification, Feature Importance Methods. Style: Strict on ML methodology.
- **R2 (Domain)**: Prof. Mei-Ling Wang — National Chengchi University. Expertise: Taiwan Higher Education Finance, University Governance. Style: Demands domain accuracy.
- **R3 (Perspective)**: Prof. James Okonkwo — University of Cape Town. Expertise: Development Economics, Education Access. Style: Global south perspective, equity lens.
- **Devil's Advocate**: Prof. Sarah Berger — MIT. Expertise: Fairness in ML, Algorithmic Decision-Making in Public Policy. Style: Fairness and accountability focus.

---

## Phase 1: Key Reviewer Findings (Abbreviated)

### EIC (Prof. Liu)

**Summary**: This paper develops a machine learning system to predict which private universities in Taiwan are at risk of closure within 5 years, using enrollment data, financial indicators, and geographic features. The best-performing model (XGBoost) achieves 87% AUC-ROC on held-out data. Feature importance analysis reveals that enrollment decline rate, debt-to-asset ratio, and geographic isolation are the strongest predictors.

**Overall**: 4 (Borderline Accept) — Useful application with decent results, but needs stronger evaluation and more careful treatment of policy implications.

### R1 Methodology (Prof. Volkov)

**Key Concerns**:
- W1: Dataset is extremely small (N=108 universities, 12 closures). With only 12 positive examples, 87% AUC-ROC is likely overfit. Need cross-validation with appropriate strategy for imbalanced data (stratified k-fold, not random split).
- W2: Feature leakage risk — some financial indicators (e.g., "special audit flag") may be consequences of closure risk, not predictors.
- W3: No comparison with simple logistic regression baseline. Complex models need to justify their complexity.
- W4: SHAP values reported but no confidence intervals on feature importance — small dataset makes these unstable.

**Overall**: 2 (Reject) — Fundamental data size concerns.

### R2 Domain (Prof. Wang)

**Key Concerns**:
- W1: Missing key institutional variables: university type (general vs. technology), founding year, religious affiliation — all known to correlate with survival.
- W2: "Closure" is poorly defined — does it include merger, consolidation, transformation into vocational school? Each is a different outcome.
- W3: Government intervention is not modeled — MOE has actively prevented some closures through mergers.

**Overall**: 3 (Borderline Reject) — Domain modeling needs significant improvement.

### R3 Perspective (Prof. Okonkwo)

**Key Insights**:
- The framework could transfer to other countries facing demographic decline (Japan, Korea, parts of Europe)
- Missing equity dimension: which communities lose access to higher education when universities close?
- Policy use case needs careful design — a "closure risk score" could become a self-fulfilling prophecy if made public

**Overall**: 4 (Borderline Accept) — Interesting direction with transferability potential if execution improves.

### Devil's Advocate (Prof. Berger)

**Strongest Counter-Argument**: A predictive model for university closure is fundamentally different from predicting weather or stock prices — it predicts an administrative decision made by human institutions (MOE, university boards). The model treats closure as a natural phenomenon when it is actually a policy choice. Universities with identical risk profiles may survive or close based on political connections, alumni advocacy, or MOE discretion. This category error undermines the entire framing.

**CRITICAL Issue**: DA-C1 — Conceptual validity: the paper treats an administrative decision as a predictable outcome without modeling the decision-making process.

**MAJOR Issues**:
- DA-M1: Fairness/equity — model could discriminate against universities serving disadvantaged populations (rural, indigenous communities)
- DA-M2: Self-fulfilling prophecy risk — publishing risk scores could accelerate closures
- DA-M3: No stakeholder analysis — what happens to students, faculty, communities?

---

## Phase 2: Editorial Decision

**Decision: 3 — Borderline Reject**

### Consensus Map

| Issue | Reviewers | Classification |
|-------|-----------|---------------|
| Dataset too small for reliable ML | R1, DA | CONSENSUS-2 (but critical) |
| Closure definition needs refinement | R2, DA | CONSENSUS-2 |
| Missing key features | R1, R2 | CONSENSUS-2 |
| Conceptual validity of prediction framing | DA (CRITICAL) | DA-CRITICAL |
| Equity/fairness concerns | R3, DA | CONSENSUS-2 |
| Transfer potential is valuable | R3, EIC | CONSENSUS-2 (positive) |

### Decision Rationale

The paper tackles an important applied problem, and the idea of predicting institutional risk is valuable. However, two fundamental issues prevent acceptance: (1) the dataset is too small for reliable ML evaluation (12 positive examples), and (2) the Devil's Advocate raises a valid CRITICAL challenge about the conceptual framing — closure is an administrative decision, not a natural event, and predicting it requires modeling the decision process, not just the risk factors.

### Revision Roadmap (Priority 1)

| # | Issue | Fix | Effort |
|---|-------|-----|--------|
| R1 | Address DA-C1: reframe from "predicting closure" to "identifying risk factors" — change the claim from prediction to risk assessment | Rewrite framing, adjust evaluation accordingly | Medium |
| R2 | Address small dataset: use proper evaluation (LOOCV or nested CV), add calibration plots, compare with logistic regression | Rerun all experiments | High |
| R3 | Define "closure" precisely and handle different outcome types | Consult MOE records, reclassify outcomes | Medium |
| R4 | Add fairness analysis: does the model disproportionately flag universities serving disadvantaged communities? | Add equity analysis section | Medium |
