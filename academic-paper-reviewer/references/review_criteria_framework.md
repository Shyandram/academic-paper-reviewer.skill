# Review Criteria Framework

Structured review criteria differentiated by paper type. Reviewers should identify the paper type first, then apply the relevant criteria.

---

## Paper Type Identification

| Paper Type | Indicators |
|-----------|-----------|
| **Empirical** | Proposes a method + evaluates on benchmarks/datasets |
| **Theoretical** | Proves theorems, derives bounds, provides formal analysis |
| **Benchmark/Survey** | Compares existing methods, introduces evaluation protocols |
| **System/Application** | Builds a working system, deploys in real-world setting |
| **Dataset** | Introduces a new dataset with collection methodology |
| **Analysis/Insight** | Provides novel understanding of existing methods/phenomena |
| **Position/Vision** | Argues for a new research direction or paradigm |

---

## Universal Criteria (Apply to All Paper Types)

### Clarity and Presentation
- Is the paper self-contained? Can an expert reader reproduce the key ideas?
- Is the writing concise and precise? (Watch for: vague claims, undefined notation, ambiguous references)
- Are figures and tables informative and well-designed?
- Is the paper well-organized with logical flow?

### Ethical Considerations
- Does the paper discuss potential negative societal impact?
- If human subjects are involved: is IRB approval mentioned?
- If personal data is used: are privacy measures described?
- Are limitations honestly disclosed?

### Reproducibility (Base Level)
- Are sufficient details provided for an expert to understand the approach?
- Are key hyperparameters, settings, and design choices documented?

---

## Type-Specific Criteria

### Empirical Papers

**Quality Criteria:**
| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| Technical Soundness | High | Is the method well-motivated and correctly derived? Are there bugs in the formulation? |
| Experimental Design | High | Fair baselines? Appropriate datasets? Sufficient ablations? |
| Statistical Rigor | High | Error bars? Multiple runs? Significance tests where appropriate? |
| Reproducibility | Medium | Code availability? Full hyperparameter specification? Hardware details? |
| Clarity of Contribution | Medium | Is it clear what is new vs. borrowed from prior work? |

**Common Pitfalls:**
- Unfair baseline comparison (old versions, wrong hyperparameters, missing strong baselines)
- Cherry-picked results (only best datasets, only favorable metrics)
- Missing ablation studies for key components
- Overclaimed generalization from limited experiments

### Theoretical Papers

**Quality Criteria:**
| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| Proof Correctness | Critical | Are proofs logically sound? Are all steps justified? |
| Assumption Reasonableness | High | Are assumptions clearly stated? Are they realistic? |
| Tightness of Bounds | Medium | How tight are the bounds? Are lower bounds provided? |
| Practical Relevance | Medium | Do theoretical insights translate to practice? |
| Empirical Validation | Medium | Is there at least some experimental verification? |

**Common Pitfalls:**
- Hidden assumptions not stated
- Proofs that only work in trivial settings
- No connection between theory and practice
- Missing comparison with existing theoretical results

### Benchmark/Survey Papers

**Quality Criteria:**
| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| Coverage | High | Are all relevant methods included? Is anything important missing? |
| Fairness | High | Same compute budget? Same hyperparameter tuning effort? Same data? |
| Reproducibility | High | Can others run the benchmark? Is code + data released? |
| Insight | High | Does the comparison reveal something non-obvious? |
| Recency | Medium | Are the most recent methods included? |

**Common Pitfalls:**
- Inconsistent evaluation protocols across methods
- Missing important recent methods
- No analysis beyond raw numbers (e.g., no computational cost comparison)
- Stale benchmark tasks that the community has moved past

### System/Application Papers

**Quality Criteria:**
| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| System Design | High | Is the architecture well-motivated? Are design decisions justified? |
| Real-World Validation | High | Is there evidence of real-world performance, not just benchmarks? |
| Scalability | Medium | Does the system scale? What are the computational costs? |
| User Study | Medium | If applicable, is there user evaluation? |
| Deployment Considerations | Medium | Latency, memory, maintenance, failure modes? |

**Common Pitfalls:**
- Only benchmark evaluation, no real-world deployment evidence
- Ignoring computational cost
- No failure mode analysis
- Missing comparison with simpler alternatives

### Dataset Papers

**Quality Criteria:**
| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| Gap Justification | High | Why is this dataset needed? What gap does it fill? |
| Collection Methodology | High | Is the data collection process well-documented and reproducible? |
| Annotation Quality | High | Inter-annotator agreement? Quality control measures? |
| Bias Analysis | High | Are potential biases identified and documented? |
| Benchmark Tasks | Medium | Are baseline results provided for meaningful tasks? |
| Data Access | Medium | Is the data publicly available? License? |

**Common Pitfalls:**
- No justification for why existing datasets are insufficient
- Weak annotation quality control
- No bias or fairness analysis
- Insufficient documentation (datasheet for datasets)

### Analysis/Insight Papers

**Quality Criteria:**
| Criterion | Weight | What to Check |
|-----------|--------|---------------|
| Novelty of Insight | High | Is the insight non-obvious and informative? |
| Evidence Quality | High | Is the analysis thorough and convincing? |
| Practical Implications | Medium | Does the insight lead to actionable recommendations? |
| Scope | Medium | How broadly does the insight apply? |

---

## Cross-Cutting Considerations

### Novelty Assessment Matrix

| Type of Novelty | Examples | Value |
|----------------|---------|-------|
| New problem formulation | Defining a task no one has formalized | High |
| New method for existing problem | Novel architecture, algorithm, or approach | High |
| New insight about existing methods | Understanding why something works/fails | High |
| Novel combination of existing techniques | If the combination is non-trivial and well-motivated | Medium-High |
| Incremental improvement | Better numbers on existing benchmarks | Low-Medium |
| New dataset for existing task | If it fills a genuine gap | Medium |
| Engineering contribution | Making something faster/cheaper without conceptual novelty | Medium |

### Red Flags (Any Paper Type)

- Results that seem too good to be true
- Missing comparison with obvious baselines
- Extremely narrow evaluation (1 dataset, 1 metric)
- Claims not supported by evidence
- Self-plagiarism or recycled content from prior publications
- Inconsistency between abstract claims and experimental results
- Missing related work that directly competes with the paper
