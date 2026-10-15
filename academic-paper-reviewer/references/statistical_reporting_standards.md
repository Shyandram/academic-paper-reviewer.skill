# Statistical Reporting Standards

Quick reference for the Methodology Reviewer when evaluating statistical rigor and reporting quality.

---

## Field-Norm Calibration (read first)

Apply these standards in proportion to the experiment's scale and the field's practice:

| Setting | Realistic expectation |
|---------|-----------------------|
| Small/medium experiments (CIFAR-scale, few-shot, fine-tuning, RL, medical datasets of hundreds to thousands of samples) | Multiple seeds (≥ 3, ideally 5) with mean ± std or CIs. Missing variance is a real weakness. |
| Large-scale training (ImageNet-scale pretraining, COCO/ADE20K detection or segmentation, video, large generative models) | A single run per configuration is common practice. Ask for variance when the claimed gain is small relative to known run-to-run noise (detection/segmentation: often ~0.2–0.5 AP/mIoU), or ask for variance on a reduced-scale proxy. Don't treat a single run alone as a High-severity flag. |
| Foundation-model / API evaluation | Variance over prompts, sampling seeds and decoding settings matters more than training seeds. |
| Theory with illustrative experiments | Statistical rigor matters less than the experiments actually testing the theory's prediction. |

The guiding question: **"Could the claimed improvement plausibly be noise?"** If yes, and the paper gives no evidence that it isn't, that is a weakness, whatever the field's norms.

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

### Foundation Model / LLM / VLM Evaluation

| Item | Required? | Notes |
|------|-----------|-------|
| Exact model versions (and API dates for closed models) | Yes | Closed APIs change silently over time |
| Prompts, few-shot exemplars, decoding parameters | Yes | Release them; report sensitivity to prompt variation |
| Contamination analysis | Yes for public benchmarks | Overlap of the test set with pretraining or fine-tuning data; prefer post-cutoff or held-out sets |
| LLM-as-judge validation | If used | Agreement with human judgments, position/length-bias controls, judge model version |
| Number of samples / attempts (pass@k, best-of-n) | Yes | Compare methods with equal sampling budgets |

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
| Comparing 2 classifiers on the same test set | McNemar's test (per-sample correctness), or paired bootstrap |
| Comparing 2 models on mAP / mIoU / FID on the same test set | Paired bootstrap over test images (resample images, recompute the metric), report a 95% CI of the difference |
| Comparing 2 models across seeds, normally distributed results | Paired t-test (pair by seed or by dataset) |
| Comparing 2 models, non-normal or small N | Wilcoxon signed-rank test |
| Comparing 3+ models | Friedman test + post-hoc Nemenyi |
| Comparing across multiple datasets | Two-way ANOVA or Friedman test |
| Results from single run | Seed-level significance testing impossible; test-set bootstrap still possible. Flag only per the Field-Norm Calibration above |
| Human preference studies (e.g., A/B for generation quality) | Binomial/sign test on preferences; report rater count, items per rater and inter-rater agreement |

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
- [ ] **Single-run results without variance where gains are small**: see the Field-Norm Calibration above
- [ ] **Test set contamination**: Evidence that hyperparameters were tuned on the test set
- [ ] **Missing obvious baselines**: No comparison with the most cited recent method
- [ ] **Selective reporting**: Results on some datasets/metrics omitted without explanation
- [ ] **p-hacking signals**: Many comparisons, only significant ones reported
- [ ] **Training details inconsistency**: Different training budgets for proposed method vs baselines
- [ ] **Data leakage**: Near-duplicate images across splits, subject/patient/scene overlap, temporal leakage in video, pretraining data containing the test set
- [ ] **Prompt / checkpoint selection on test data**: Choosing the prompt, checkpoint or threshold that maximizes test performance

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

## Reporting Conventions (Tables and Figures)

### Numbers
- Report the same number of decimals per metric throughout (e.g., mIoU to 1 decimal, PSNR to 2).
- Report mean ± std (state *n*) or 95% CIs. For significance tests, give the test name, the statistic and the exact p-value.
- Give relative and absolute improvements unambiguously: "+1.2 mIoU (absolute)" and not "+3% improvement".

### Tables
- Caption above (or below, following the venue template), and say what is bold or underlined (best / second best).
- Group rows by comparable settings (backbone, pretraining data, resolution, extra data). Mark rows reproduced by the authors (†) versus copied from papers.
- Make the efficiency columns (params, FLOPs, latency) and their measurement conditions explicit.

### Figures
- Label all axes with units. Show error bars or shaded regions for means.
- Use colorblind-friendly palettes that still read in grayscale.
- Qualitative comparisons: same input, crop and resolution for every method; state how the examples were selected (random vs. curated).
- Don't use truncated y-axes that exaggerate small gains without saying so.

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
| Same backbone & pretraining data | Gains from a stronger backbone or more pretraining data (e.g., ImageNet-22k vs. 1k, web-scale vs. curated) are not method gains |
| Same test-time tricks | TTA, multi-scale testing, ensembling, sliding window applied to all methods or none |
| Same extra data / labels | Extra training data, pseudo-labels or additional annotation types disclosed and matched |
| Efficiency measured identically | Same hardware, batch size, precision (FP32/FP16/INT8), resolution and software stack for latency |
