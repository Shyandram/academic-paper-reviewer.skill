# Example: Full Review of a Computer Vision Paper

> **Illustrative example.** The paper, reviewers, numbers and findings below are entirely fictional. They demonstrate format, depth and calibration. Baselines are described generically on purpose, so no real method's results are misrepresented. The aggregated scores are the actual output of `scripts/aggregate_scores.py` on `scripts/example_scores.json`.

**Fictional paper**: *"AdaPrune-Seg: Content-Adaptive Token Pruning for Real-Time Semantic Segmentation with Vision Transformers"*. Target venue: CVPR (inferred from the template).

---

## Phase 0: Reviewer Configuration Card

| Item | Finding |
|------|---------|
| Primary Discipline | Computer Vision → Semantic Segmentation |
| Secondary Discipline(s) | Efficient Deep Learning, Model Compression |
| Paper Type | Empirical (composite weights: empirical) |
| Core Technique(s) | Vision Transformers, dynamic token pruning |
| Target Venue | CVPR (inferred from the LaTeX template) |
| Paper Maturity | Submission-ready |
| Ethics-Relevant Content | Driving-scene data only; no human-subject data |

**Claimed contributions**: (C1) a learned, content-adaptive token-pruning module for dense prediction; (C2) a token-restoration decoder that recovers full-resolution outputs; (C3) "2.1× faster than the strongest ViT segmenters at comparable accuracy" on ADE20K and Cityscapes.

**Review team (fictional personas)**
- **EIC**: Dr. Ilse Marquardt, vision group, large public research university (Europe). Dense prediction, efficient architectures. Style: weighs efficiency claims against real deployment value.
- **R1 (Methodology)**: Dr. Tomás Okafor-Reyes, industrial research lab (North America). Token pruning and merging, latency benchmarking. Style: insists on measured latency under matched settings.
- **R2 (Domain)**: Prof. Hye-jin Baek, vision lab, public research university (East Asia). Semantic segmentation architectures and benchmarks. Style: thorough on positioning against recent segmenters.
- **R3 (Perspective)**: Dr. Arjun Venkataraman, embedded-systems group, technical university (South Asia). Hardware-aware ML, edge accelerators. Style: asks what runs on real devices.
- **Devil's Advocate**: Dr. Noor Haddad, evaluation-methodology group, research institute (Middle East). Benchmarking methodology, confound analysis. Style: rigorous skeptic.

---

## Phase 1: Reports (abbreviated)

### EIC (Dr. Marquardt): Overall 4, Confidence 5
**Summary**: The paper proposes a learned module that drops low-information tokens in intermediate ViT layers and a lightweight decoder that restores dropped positions for dense output. On ADE20K and Cityscapes it reports accuracy comparable to strong ViT segmenters at roughly half the latency.
**Strengths**: a relevant problem for real-time segmentation; a simple, well-explained module (§3.2, Fig. 2); a clear accuracy–speed trade-off curve (Fig. 5).
**Weaknesses**: W1, the speedup is reported on a single GPU type at batch size 1 only (Table 4); W2, novelty relative to existing token-pruning work for *classification* needs to be argued more sharply (§2).
**Quality 3 · Clarity 3 · Significance 3 · Originality 2.**

### R1 Methodology (Dr. Okafor-Reyes): Overall 3, Confidence 5
- **W1 (comparison fairness)**: Table 2 compares AdaPrune-Seg at 640×640 against the baselines' published 512×512 numbers. The resolution mismatch alone could explain the accuracy parity. *Fix*: rerun the two strongest baselines at 640×640, or report AdaPrune-Seg at 512×512.
- **W2 (latency methodology)**: latency is measured in FP16 for the proposed method, but the precision for the baselines is not stated (§4.1). *Fix*: state the precision, framework and batch size for all rows; add batch-8 and an edge device.
- **W3 (variance)**: the +0.4 mIoU over the pruning-free baseline (Table 3) is a single run, within typical run-to-run noise. *Fix*: 3 seeds for the Table 3 ablation (≈ 60 GPU-hours).
- **Recomputed**: the claimed "2.1×" equals 41 ms / 19.6 ms ≈ 2.09× from Table 4. Consistent.

### R2 Domain (Prof. Baek): Overall 4, Confidence 4
- **W1**: Related Work covers token pruning for classification but misses token *merging* approaches adapted to dense prediction, which are the closest competitors. *Fix*: add an empirical comparison with at least one training-free token-merging method applied to the same backbone.
- **W2**: The restoration decoder resembles existing feature-upsampling decoders. Clarify what differs (§3.3).
- **Missing references**: described by line of work rather than invented titles. Critical: token-merging methods applied to segmentation. Important: dynamic-resolution or early-exit segmentation methods.

### R3 Perspective (Dr. Venkataraman): Overall 4, Confidence 3
- Irregular token sets are hard to accelerate on edge NPUs, which expect static shapes. GPU speedups may not transfer. *Fix*: report one static-shape deployment (e.g., fixed keep-ratio buckets) on an embedded device.
- Opportunity: the pruning masks could double as a compute-saliency signal for camera ISP or region-of-interest encoding.
- Ethics: low risk; suggests discussing failure on small, safety-critical objects (pedestrians far away).

### Devil's Advocate (Dr. Haddad): Overall 3, Confidence 4
**Steelman**: if content-adaptive pruning preserves accuracy at half the cost, it is a practical win for every ViT segmenter.
**Strongest counter-argument**: the headline claim (C3) rests on Table 2, where the proposed model uses higher input resolution *and* a longer training schedule (160k vs. 80k iterations, Appendix B) than the copied baseline numbers. The "comparable accuracy" may come from these two advantages, with pruning actually *costing* accuracy that the extra resolution and schedule hide. The latency comparison then pits a pruned high-resolution model against unpruned baselines whose own speed was measured under unknown conditions. Nothing in the paper separates the pruning contribution from these confounds.
- **DA-C1 (CRITICAL; resolvable by: new experiments)**: confounded main comparison (Table 2 + Appendix B). *Fix*: matched-setting comparison (same resolution and schedule) for at least the two strongest baselines.
- **DA-M1 (MAJOR)**: small-object accuracy is not reported; pruning likely hurts thin and small classes (per-class IoU missing).
- **DA-m1 (MINOR)**: Fig. 6 qualitative examples are not stated as random.

---

## Phase 2: Editorial Decision

### Aggregated scores (output of `scripts/aggregate_scores.py`)

| Dimension | EIC | R1 (Meth.) | R2 (Domain) | R3 (Persp.) | DA | Weighted Avg | Spread |
|---|---|---|---|---|---|---|---|
| Technical Rigor | 68 | 58 | 66 | 70 | 52 | 62.6 | 18 |
| Clarity & Presentation | 78 | 74 | 76 | 80 | 75 | 76.4 | 6 |
| Novelty & Originality | 62 | 60 | 55 | 68 | 58 | 60.4 | 13 |
| Significance & Impact | 66 | 64 | 68 | 74 | 60 | 66.0 | 14 |
| Experimental Validation | 60 | 48 | 60 | 62 | 42 | 54.1 | 20 |
| Reproducibility | 70 | 62 | 66 | 68 | 64 | 65.9 | 8 |
| Ethical Compliance | 72 | 70 | 72 | 58 | 66 | 68.2 | 14 |
| **Composite** | 66.8 | 60.4 | 65.0 | 68.3 | 57.0 | **63.4** | |

**Composite-implied decision**: 4 (Borderline Accept)
**DA-CRITICAL cap**: DA-C1 upheld; it needs new experiments → cap = 3 (Borderline Reject)
**Final decision**: **3, Borderline Reject**. The composite alone would suggest 4, but the headline claim is not yet separable from the resolution and schedule confounds. Experimental Validation has the largest spread (20): R1 and the DA weigh the confound heavily, while the EIC and R3 credit the trade-off curve. The editor sides with R1 and the DA, because C3 is the paper's main claim.

### Cross-Venue Outlook (user asked "compare venues")

Output of `python3 scripts/aggregate_scores.py scripts/example_scores.json --venue cvpr --venue iclr --venue icml --venue acmmm --venue tmlr --venue tpami`:

| Venue | Venue-weighted composite | Bar offset | Band before → after DA cap | Venue recommendation | Venue sub-scores | Scale status |
|---|---|---|---|---|---|---|
| CVPR (2026) | 62.7 | +0 | 4 → 3 | 3 Borderline Reject | — | confirmed |
| ICLR (2026) | 63.3 | +0 | 4 → 3 | 4 on {0,2,4,6,8,10} (5 on {1,3,5,6,8,10}) | Soundness 2, Presentation 3, Contribution 2 | secondary |
| ICML (2025) | 63.0 | +0 | 4 → 3 | 2 Weak reject (leaning reject) | — | official |
| ACM Multimedia (2026) | 63.3 | +0 | 4 → 3 | Weak reject | — | unpublished |
| TMLR (2025) | 63.2 | -5 | 4 → 3 | Reject (or major changes: narrow claims / add evidence) | Claims & evidence No, Audience interest Yes | official |
| IEEE TPAMI (2025) | 63.0 | +3 | 4 → 3 | Major Revision | — | secondary |

**Editor's venue advice**: DA-C1 blocks every venue; no choice of venue gets around it. Once a matched-setting comparison is added, the "before cap" column applies: band 4 at every venue, though only just at TPAMI (63.0 against a raised bar of 63). CVPR and ICCV remain the natural fit for a segmentation-efficiency paper. TMLR becomes attractive if the authors narrow C3 to what the matched comparison supports, because TMLR doesn't penalize modest gains. ACM MM would need a multimedia angle (e.g., video streaming or on-device AR) to pass its scope gate. A TPAMI submission would need the edge-device study and a broader set of backbones.

### DA-CRITICAL ruling
DA-C1 is **upheld**. Verified against Table 2 and Appendix B. R1-W1 independently raised the resolution part (merged: DA-C1 + R1-W1).

### Revision Roadmap (Priority 1)

| # | Issue | Source IDs | Location | Fix | Effort | Rebuttal-feasible? |
|---|-------|-----------|----------|-----|--------|--------------------|
| R1 | Confounded main comparison (resolution, schedule) | DA-C1, R1-W1 | Table 2, App. B | Matched 512² / 80k comparison vs. 2 strongest baselines | High (~150 GPU-h) | Partially (one baseline) |
| R2 | Latency measured under unstated, possibly mismatched conditions | R1-W2, EIC-W1 | Table 4, §4.1 | Same precision/framework/batch for all rows; add batch-8 | Low | Yes |
| R3 | Missing closest competitors (token merging for dense prediction) | R2-W1 | §2, Table 2 | Add ≥ 1 empirical comparison | Medium | Yes |

**Priority 2**: per-class IoU / small-object analysis (DA-M1); 3-seed ablation (R1-W3); edge-device static-shape deployment (R3); decoder novelty clarification (R2-W2).
**Priority 3**: random qualitative samples (DA-m1); ISP/ROI-encoding discussion (R3).

### Excerpt of the decision letter
> … Reviewers agree that the problem is important and that the pruning module is simple and clearly presented (EIC, R2, R3). The central concern, raised by the Devil's Advocate (DA-C1) and independently by Reviewer 1 (W1), is that the main comparison in Table 2 differs from the baselines in input resolution and training schedule, so the contribution of pruning itself cannot yet be isolated. A matched-setting comparison would directly resolve this and could change the outcome …
