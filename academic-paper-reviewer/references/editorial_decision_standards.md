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
| Majority Accept + upheld DA-CRITICAL | Borderline Accept (4) at best; Borderline Reject (3) if the fix needs new data/experiments |
| Mixed: 2 Accept + 2 Reject + 1 Borderline | Requires arbitration → typically Borderline (3–4) |
| Majority Borderline (3–4) | Borderline Accept (4) or Borderline Reject (3) based on DA |
| 3+ Reject (1–2) | Reject (2) |
| Any reviewer: Strong Reject + valid justification | Discuss carefully; likely Reject (2) |
| Upheld DA-CRITICAL present | Cannot be Accept (5–6); see the DA-CRITICAL Ceiling below |

### Weighted Score Thresholds (Guideline, Not Absolute)

| Weighted Avg (0–100) | Typical Decision Range |
|----------------------|----------------------|
| ≥ 85 | Strong Accept (6) |
| 70–84 | Accept (5) |
| 60–69 | Borderline Accept (4) |
| 50–59 | Borderline Reject (3) |
| 35–49 | Reject (2) |
| < 35 | Strong Reject (1) |

These thresholds are guidelines. The decision should be justified by the review content, not just the numbers. A paper with a weighted average of 72 and an upheld DA-CRITICAL issue is never Accept.

### DA-CRITICAL Ceiling (hard rule)

| Upheld DA-CRITICAL issues | Maximum decision |
|---------------------------|------------------|
| None | No ceiling (decide on content and composite) |
| All resolvable by clarification or minor additions (rewording claims, adding existing details, small analyses on existing results) | **Borderline Accept (4)** |
| At least one needs new data, new experiments or a redesign | **Borderline Reject (3)** |

The synthesizer may downgrade a DA-CRITICAL issue to MAJOR only with a written justification tied to the manuscript. The decision may always be *lower* than the ceiling.

### Conference ↔ Journal Mapping

| Overall (1–6) | Journal recommendation | Notes |
|---------------|------------------------|-------|
| 6 Strong Accept | Accept (as is or with trivial edits) | |
| 5 Accept | Minor Revision | Journals rarely accept without any revision |
| 4 Borderline Accept | Minor Revision, or Major Revision if Priority 1 items need new experiments | |
| 3 Borderline Reject | Major Revision | Journals give a revision path where a conference would reject |
| 2 Reject | Reject (resubmission possible after substantial new work) | Major Revision only if the fix path is clear and bounded |
| 1 Strong Reject | Reject | |

---

## Special Decision Considerations

### Venue Tier Calibration

Different venues have different acceptance standards:

| Venue Tier | Examples | Typical Accept Rate (approx.) | Calibration |
|-----------|----------|-------------------|-------------|
| Top-tier conference | CVPR, ICCV, ECCV, NeurIPS, ICLR, ICML | ~20–30% | High bar: clear novelty, strong controlled evaluation, convincing ablations |
| Top-tier journal | TPAMI, IJCV, Nature-family journals | Selective | Top-conference bar *plus* completeness, depth and long-term value; extended versions of conference papers need substantial new content |
| Strong | AAAI, IJCAI, TIP, TMLR, MICCAI (for medical imaging) | ~25–35% | Sound and clearly useful; more tolerance for niche or application contributions (TMLR explicitly emphasizes correctness over novelty) |
| Mid-tier | BMVC, WACV, ACCV, domain journals | ~30–45% | Sound work with a clear contribution suffices |
| Workshop | CVPR/ICCV/NeurIPS workshops | ~50–70% | Work in progress is acceptable if the direction is promising |

Acceptance rates vary by year; treat them as orientation, not targets. See `references/venue_profiles.md` for review-form conventions.

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
