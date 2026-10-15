# Editorial Decision Standards

Criteria and decision matrix for Accept/Minor Revision/Major Revision/Reject decisions.

---

## Overall Score Definitions (1–6 Scale)

### 6 — Strong Accept
**Technically flawless paper with groundbreaking impact.**
- No reviewers identified serious technical flaws
- Contribution is significant and clearly advances the field
- Evaluation is exceptionally strong and comprehensive
- Reproducibility is excellent (code + data + detailed methodology)
- No unaddressed ethical considerations
- Writing is exemplary
- This score should be rare — reserved for truly exceptional work

### 5 — Accept
**Technically solid paper with high impact.**
- Methods are sound and well-validated
- High impact on at least one sub-area, or moderate-to-high impact across multiple areas
- Good to excellent evaluation with appropriate baselines
- Sufficient reproducibility information
- No unaddressed ethical concerns
- Writing is clear and well-organized
- Minor issues may exist but don't undermine the contribution

### 4 — Borderline Accept
**Technically solid, reasons to accept outweigh reasons to reject.**
- Core technical approach is sound
- Contribution is meaningful but may have limited scope
- Evaluation may have gaps but covers the essential cases
- Some weaknesses exist but are addressable
- Use sparingly — this is for papers where you lean toward acceptance despite reservations
- Typical issues: limited evaluation, missing one important baseline, narrow scope

### 3 — Borderline Reject
**Technically solid, reasons to reject outweigh reasons to accept.**
- Core approach may be sound but execution has gaps
- Contribution may be incremental or unclear
- Evaluation has notable weaknesses (missing baselines, limited datasets)
- Use sparingly — this is for papers where you lean toward rejection despite merits
- Typical issues: insufficient novelty, evaluation doesn't fully support claims, overclaimed results

### 2 — Reject
**Paper with significant issues.**
- Technical flaws that undermine the claims
- Weak evaluation that doesn't validate the contribution
- Inadequate reproducibility
- Incompletely addressed ethical considerations
- May be work in progress rather than a complete contribution

### 1 — Strong Reject
**Paper with fundamental problems.**
- Well-known results presented as novel
- Serious unaddressed ethical considerations
- Multiple significant technical flaws
- Results that cannot be trusted

---

## Decision Matrix

This matrix helps map reviewer consensus to editorial decisions.

### Mapping Reviewer Scores to Decision

| Reviewer Consensus Pattern | Recommended Decision |
|---------------------------|---------------------|
| All 5 reviewers: Accept (5–6) | Strong Accept (6) |
| 4 Accept + 1 Borderline | Accept (5) |
| 3 Accept + 2 Borderline | Accept (5) |
| Majority Accept + DA-CRITICAL | Borderline Accept (4) at best |
| Mixed: 2 Accept + 2 Reject + 1 Borderline | Requires arbitration → typically Borderline (3–4) |
| Majority Borderline (3–4) | Borderline Accept (4) or Borderline Reject (3) based on DA |
| 3+ Reject (1–2) | Reject (2) |
| Any reviewer: Strong Reject + valid justification | Discuss carefully; likely Reject (2) |
| DA-CRITICAL present | Cannot be Accept (5–6); maximum is Borderline Accept (4) |

### Weighted Score Thresholds (Guideline, Not Absolute)

| Weighted Avg (0–100) | Typical Decision Range |
|----------------------|----------------------|
| ≥ 85 | Strong Accept (6) |
| 70–84 | Accept (5) |
| 60–69 | Borderline Accept (4) |
| 50–59 | Borderline Reject (3) |
| 35–49 | Reject (2) |
| < 35 | Strong Reject (1) |

These thresholds are guidelines. The decision should be justified by the review content, not just the numbers. A paper with a weighted average of 72 but a DA-CRITICAL issue should not be scored Accept.

---

## Special Decision Considerations

### Venue Tier Calibration

Different venues have different acceptance standards:

| Venue Tier | Typical Accept Rate | Calibration |
|-----------|-------------------|-------------|
| Top-tier (CVPR, NeurIPS, ICML, Nature) | 20–25% | High bar: need clear novelty + strong evaluation |
| Strong (ECCV, ICCV, AAAI, IJCAI) | 25–30% | Similar to top-tier, slightly more tolerance for niche contributions |
| Mid-tier (BMVC, WACV, domain-specific) | 30–40% | Sound work with clear contribution suffices |
| Workshop | 50–70% | Work in progress acceptable if direction is promising |

### Rebuttal Potential

When scoring borderline papers, consider whether the identified issues are:
- **Fixable in rebuttal** (additional experiments, clarifications): Lean toward higher score
- **Fundamental** (wrong approach, insufficient novelty): Lean toward lower score
- **Time-consuming** (requires new data collection, major redesign): Lean toward lower score but note in decision

### Double Standards to Avoid

- Don't hold ML-applied-to-X papers to a lower standard than core ML papers (or vice versa)
- Don't penalize negative results or replication studies — they have value if well-executed
- Don't require novelty in every dimension — a paper can contribute meaningfully through excellent evaluation of existing methods
- Don't confuse "I wouldn't have done it this way" with "this is wrong"

---

## Decision Letter Writing Guide

### Structure
1. **Opening**: Thank the authors, acknowledge the topic
2. **Strengths first**: Always start with what the reviewers found positive
3. **Concerns**: Present in order of importance (CRITICAL → MAJOR → MINOR)
4. **Decision**: State clearly with brief justification
5. **Path forward**: If not Accept, what would change the decision?

### Tone
- Professional and respectful, even for strong rejections
- Constructive — every criticism paired with a path to improvement
- Honest — don't soften a Reject to sound like a Borderline Accept
- Balanced — acknowledge the work that went into the paper

### Common Mistakes in Decision Letters
- Being vague about what needs to change
- Not distinguishing required changes from suggestions
- Focusing only on negatives without acknowledging strengths
- Making the decision seem arbitrary rather than evidence-based
- Contradicting the reviewers without explanation
