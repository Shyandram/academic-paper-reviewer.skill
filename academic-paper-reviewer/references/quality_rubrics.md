# Quality Rubrics

Calibrated 0–100 scoring rubrics for the 7 review dimensions. All reviewers must use these rubrics when assigning dimension scores.

---

## How to Use These Rubrics

1. **Read the descriptor for each level** (Exceptional → Inadequate)
2. **Select the level that best matches** the paper for each dimension
3. **Assign a score within that band** — use the full range, not just the midpoint
4. **Write a brief rationale** referencing specific evidence from the paper

---

## Dimension 1: Technical Rigor

| Band | Score Range | Descriptor | Characteristics |
|------|-----------|------------|-----------------|
| Exceptional | 90–100 | Flawless technical execution | Proofs are complete and elegant; experiments are airtight; methodology is state-of-the-art; all claims fully supported; no technical errors found |
| Strong | 75–89 | Minor gaps only | Sound methodology with small gaps; most claims well-supported; minor technical issues that don't undermine conclusions |
| Competent | 55–74 | Adequate with notable gaps | Core approach is sound but has meaningful gaps; some claims not fully supported; methodology is standard but correctly applied |
| Developing | 30–54 | Significant weaknesses | Multiple technical issues; some claims unsupported; methodology has notable flaws that partially undermine conclusions |
| Inadequate | 0–29 | Fundamental flaws | Incorrect proofs, serious bugs in methodology, claims contradicted by results, or fundamentally flawed approach |

## Dimension 2: Clarity & Presentation

| Band | Score Range | Descriptor | Characteristics |
|------|-----------|------------|-----------------|
| Exceptional | 90–100 | Publication-ready excellence | Beautifully written; perfect organization; all notation defined; figures are informative and well-designed; a joy to read |
| Strong | 75–89 | Clear and well-organized | Well-written with minor issues; good structure; figures generally effective; sufficient detail for reproduction |
| Competent | 55–74 | Understandable with effort | Generally clear but requires re-reading some sections; organization could improve; some notation inconsistencies |
| Developing | 30–54 | Difficult to follow | Significant clarity issues; poor organization; missing important details; figures hard to interpret |
| Inadequate | 0–29 | Cannot be understood | Incomprehensible writing; chaotic organization; critical information missing; reader cannot evaluate the work |

## Dimension 3: Novelty & Originality

| Band | Score Range | Descriptor | Characteristics |
|------|-----------|------------|-----------------|
| Exceptional | 90–100 | Paradigm-shifting | Introduces a fundamentally new concept, framework, or approach; opens a new research direction |
| Strong | 75–89 | Clearly novel | Significant new contribution; clear differentiation from prior work; non-obvious insights or methods |
| Competent | 55–74 | Incrementally novel | Meaningful but incremental advance; novel combination of existing ideas; useful but expected extension |
| Developing | 30–54 | Limited novelty | Minor variations on existing work; contribution is primarily engineering; limited new insight |
| Inadequate | 0–29 | Not novel | Previously published results; trivial extension; no new insight or method |

## Dimension 4: Significance & Impact

| Band | Score Range | Descriptor | Characteristics |
|------|-----------|------------|-----------------|
| Exceptional | 90–100 | Transformative impact | Will change how people think about or work on this problem; broadly applicable; major advance |
| Strong | 75–89 | High impact | Likely to be widely cited and used; advances the field meaningfully; practical or theoretical value is clear |
| Competent | 55–74 | Moderate impact | Useful contribution to a sub-area; some people will build on this; narrow but real impact |
| Developing | 30–54 | Limited impact | Niche contribution; few people likely to use or cite; incremental advance in a small area |
| Inadequate | 0–29 | No impact | Does not advance the field; results are not useful; no one is likely to build on this |

## Dimension 5: Experimental Validation

| Band | Score Range | Descriptor | Characteristics |
|------|-----------|------------|-----------------|
| Exceptional | 90–100 | Comprehensive and rigorous | Multiple datasets, comprehensive ablations, fair baselines, statistical rigor, qualitative + quantitative analysis, failure case analysis |
| Strong | 75–89 | Thorough with minor gaps | Good dataset coverage; appropriate baselines; some ablations; minor missing experiments that don't undermine conclusions |
| Competent | 55–74 | Adequate | Standard evaluation setup; some baselines; limited ablations; enough to support main claims but not comprehensive |
| Developing | 30–54 | Insufficient | Missing important baselines; limited datasets; no ablation; results don't fully support claims |
| Inadequate | 0–29 | Severely lacking | Toy experiments only; no meaningful baselines; results cannot be trusted; evaluation doesn't test the claims |

## Dimension 6: Reproducibility

| Band | Score Range | Descriptor | Characteristics |
|------|-----------|------------|-----------------|
| Exceptional | 90–100 | Fully reproducible | Code released, documented, and tested; all hyperparameters specified; hardware details included; data available; random seeds fixed |
| Strong | 75–89 | Largely reproducible | Most implementation details present; code promised or available; hyperparameters mostly specified |
| Competent | 55–74 | Partially reproducible | Key details present but some gaps; an expert could likely reproduce with effort |
| Developing | 30–54 | Difficult to reproduce | Significant missing details; no code; important hyperparameters unspecified |
| Inadequate | 0–29 | Cannot be reproduced | Insufficient information to understand the method, let alone reproduce it |

## Dimension 7: Ethical Compliance

| Band | Score Range | Descriptor | Characteristics |
|------|-----------|------------|-----------------|
| Exceptional | 90–100 | Exemplary ethical consideration | Thorough impact statement; bias analysis; privacy measures documented; limitations honestly discussed; dual-use considered |
| Strong | 75–89 | Good ethical awareness | Impact discussed; key ethical issues addressed; limitations acknowledged |
| Competent | 55–74 | Basic compliance | Limitations mentioned; no major ethical oversights; minimal but adequate discussion |
| Developing | 30–54 | Incomplete | Missing limitation discussion; potential negative impacts not mentioned; ethical considerations overlooked |
| Inadequate | 0–29 | Ethical concerns | Active harm potential unaddressed; data misuse; undisclosed conflicts; human subjects concerns |

---

## Composite Score Calculation

### Weighted Aggregation Formula

The composite score is a weighted average of the 7 dimensions. Weights vary by paper type:

#### Empirical Papers (default)
```
Composite = 0.20 × Technical_Rigor
          + 0.10 × Clarity
          + 0.15 × Novelty
          + 0.15 × Significance
          + 0.20 × Experimental_Validation
          + 0.10 × Reproducibility
          + 0.10 × Ethical_Compliance
```

#### Theoretical Papers
```
Composite = 0.30 × Technical_Rigor
          + 0.10 × Clarity
          + 0.20 × Novelty
          + 0.15 × Significance
          + 0.10 × Experimental_Validation
          + 0.05 × Reproducibility
          + 0.10 × Ethical_Compliance
```

#### Dataset Papers
```
Composite = 0.15 × Technical_Rigor
          + 0.10 × Clarity
          + 0.10 × Novelty
          + 0.20 × Significance
          + 0.15 × Experimental_Validation
          + 0.15 × Reproducibility
          + 0.15 × Ethical_Compliance
```

#### System/Application Papers
```
Composite = 0.20 × Technical_Rigor
          + 0.10 × Clarity
          + 0.10 × Novelty
          + 0.20 × Significance
          + 0.20 × Experimental_Validation
          + 0.10 × Reproducibility
          + 0.10 × Ethical_Compliance
```

### Decision Mapping

| Composite Score | Typical Decision |
|----------------|-----------------|
| ≥ 85 | Strong Accept (6) |
| 70–84 | Accept (5) |
| 60–69 | Borderline Accept (4) |
| 50–59 | Borderline Reject (3) |
| 35–49 | Reject (2) |
| < 35 | Strong Reject (1) |

**Important**: These are guidelines, not hard rules. The Editorial Synthesizer should use judgment and the qualitative content of reviews to make the final decision. A paper with a composite of 72 but a DA-CRITICAL issue should not be scored Accept.

---

## Confidence Score Weighting

When aggregating across reviewers, weight by confidence:

| Confidence Level | Weight |
|-----------------|--------|
| 5 (Absolutely certain) | 1.00 |
| 4 (Confident) | 0.85 |
| 3 (Fairly confident) | 0.70 |
| 2 (Willing to defend) | 0.55 |
| 1 (Best guess) | 0.40 |

Formula:
```
Weighted_Dim_Score = Σ(reviewer_score_i × confidence_weight_i) / Σ(confidence_weight_i)
```
