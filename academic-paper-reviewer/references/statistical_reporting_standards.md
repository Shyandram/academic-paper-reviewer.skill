# Statistical Reporting Standards

Quick reference for the Methodology Reviewer when evaluating statistical rigor and reporting quality.

---

## Minimum Reporting Requirements by Study Type

### Supervised Learning Experiments

| Item | Required? | Notes |
|------|-----------|-------|
| Mean ± std across multiple runs | Yes | Minimum 3 runs with different seeds; 5+ preferred |
| Random seeds specified | Yes | Fixed seeds for reproducibility |
| Train/val/test split specification | Yes | Ratios and method (random, stratified, k-fold) |
| Hyperparameter selection method | Yes | Grid search, random search, Bayesian, manual? |
| Validation strategy | Yes | How were hyperparameters tuned? On which split? |
| All metrics relevant to the task | Yes | See task-specific metrics below |
| Computational cost | Recommended | GPU hours, hardware specs, training time |
| Confidence intervals | Recommended | 95% CI preferred over just std |
| Statistical significance tests | For close results | When improvement is small or borderline |

### Generative Model Experiments

| Item | Required? | Notes |
|------|-----------|-------|
| FID / IS / other generative metrics | Yes | Multiple metrics — FID alone is insufficient |
| Sample size for metric computation | Yes | FID is sensitive to sample size |
| Qualitative results | Yes | Cherry-picked + random samples |
| User study (for perceptual quality) | Recommended | Especially if claiming perceptual improvement |
| Diversity metrics | Recommended | Mode collapse detection |

### Reinforcement Learning Experiments

| Item | Required? | Notes |
|------|-----------|-------|
| Learning curves (not just final performance) | Yes | Show training stability |
| Multiple seeds (5+ strongly recommended) | Yes | RL is notoriously high-variance |
| Shaded regions showing variance | Yes | On learning curve plots |
| Environment versions specified | Yes | Exact version of gym/environment |
| Evaluation episodes | Yes | Number and conditions |

---

## Task-Specific Metric Requirements

### Classification
- Accuracy (if classes balanced)
- F1, Precision, Recall (if classes imbalanced)
- Confusion matrix or per-class breakdown (if applicable)
- AUC-ROC (for binary or ranking scenarios)

### Object Detection
- mAP (COCO-style: AP, AP50, AP75, APs, APm, APl)
- Inference speed (FPS or ms/image)
- Parameter count and FLOPs

### Semantic Segmentation
- mIoU (mean Intersection over Union)
- Per-class IoU for major classes
- Frequency-weighted IoU (optional)
- Dice coefficient (especially in medical imaging)

### Image Generation
- FID (Fréchet Inception Distance) — lower is better
- IS (Inception Score) — higher is better, but has known limitations
- LPIPS (Learned Perceptual Image Patch Similarity)
- SSIM / PSNR (for image reconstruction / super-resolution)

### NLP Tasks
- BLEU, ROUGE, METEOR (for generation)
- Exact Match, F1 (for QA)
- Accuracy, F1 (for classification)
- Perplexity (for language modeling)
- Human evaluation scores (for open-ended generation)

---

## Statistical Tests Quick Reference

### When to Use What

| Situation | Recommended Test |
|-----------|-----------------|
| Comparing 2 models, normally distributed results | Paired t-test |
| Comparing 2 models, non-normal or small N | Wilcoxon signed-rank test |
| Comparing 3+ models | Friedman test + post-hoc Nemenyi |
| Comparing across multiple datasets | Two-way ANOVA or Friedman test |
| Results from single run | Cannot do significance testing — this is a red flag |

### Multiple Comparison Correction

When comparing against many baselines simultaneously, p-values need correction:
- **Bonferroni**: Conservative but simple. Divide α by number of comparisons.
- **Holm-Bonferroni**: Less conservative, step-down procedure.
- **Benjamini-Hochberg**: Controls false discovery rate, good for exploratory analysis.

If a paper makes 10+ pairwise comparisons without correction, flag this.

---

## Red Flag Checklist

These are common statistical problems to watch for:

### High-Severity Red Flags
- [ ] **Single-run results without variance**: Results reported from a single random seed
- [ ] **Test set contamination**: Evidence that hyperparameters were tuned on the test set
- [ ] **Missing obvious baselines**: No comparison with the most cited recent method
- [ ] **Selective reporting**: Results on some datasets/metrics omitted without explanation
- [ ] **p-hacking signals**: Many comparisons, only significant ones reported
- [ ] **Training details inconsistency**: Different training budgets for proposed method vs baselines

### Medium-Severity Red Flags
- [ ] **Insufficient runs**: Only 2 runs (3 is minimum, 5 is preferred)
- [ ] **Missing error bars**: Results tables without standard deviations
- [ ] **Unfair compute comparison**: Proposed method uses more compute than baselines
- [ ] **Only best-result reporting**: "Best of N runs" instead of "Mean of N runs"
- [ ] **Missing training curves**: No evidence of convergence

### Low-Severity Red Flags
- [ ] **Missing FLOPs/parameter comparison**: Especially for efficiency claims
- [ ] **No failure case analysis**: Only showing success cases
- [ ] **Incomplete hardware specification**: GPU type mentioned but not training time
- [ ] **Missing data statistics**: Dataset size/distribution not fully described

---

## APA 7th Edition Quick Reference (for Reporting)

### Numbers and Statistics
- Use numerals for: statistical values (M = 4.5), measurements, percentages, ratios
- Report exact p-values (p = .032), not just p < .05
- Report effect sizes alongside significance tests
- Use consistent decimal places (2 for correlations, 3 for p-values)

### Table Formatting
- Title above, notes below
- Horizontal rules only (top, header separator, bottom — no vertical lines)
- Bold the best result in comparison tables
- Use * for statistical significance markers, defined in table notes

### Figure Formatting
- Label all axes with units
- Include error bars when showing means
- Use colorblind-friendly palettes
- Ensure readability in grayscale (for print)

---

## Evaluation Protocol Fairness Checklist

When assessing whether baselines are fairly compared:

| Check | What to Look For |
|-------|-----------------|
| Same data | All methods trained on identical data splits |
| Same preprocessing | Identical data augmentation and preprocessing |
| Same compute budget | Similar training time / iterations / epochs |
| Same tuning effort | Comparable hyperparameter search effort |
| Correct implementation | Official code or verified reimplementation |
| Recent versions | Latest available version of baseline methods |
| Same evaluation protocol | Identical test conditions (resolution, batch size, etc.) |
