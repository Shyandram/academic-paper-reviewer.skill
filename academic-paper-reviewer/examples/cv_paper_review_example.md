# Example: Full Review of a Computer Vision Paper

> **Illustrative example.** The paper, reviewers, numbers and findings below are entirely fictional. They demonstrate format, depth and calibration. Baselines are described generically on purpose, so no real method's results are misrepresented. The score tables are the actual output of `scripts/aggregate_scores.py` on `scripts/example_scores.json`.

**Fictional paper**: *"AdaPrune-Seg: Content-Adaptive Token Pruning for Real-Time Semantic Segmentation with Vision Transformers"*. Target venue: CVPR (inferred from the template).

---

## Phase 0: Reviewer Configuration Card

| Item | Finding |
|------|---------|
| Primary Discipline | Computer Vision → Semantic Segmentation |
| Secondary Discipline(s) | Efficient Deep Learning, Model Compression |
| Paper Type | Empirical (composite weights: empirical) |
| Core Technique(s) | Vision Transformers, dynamic token pruning |
| Target Venue | CVPR (inferred from the LaTeX template); profile key `cvpr` |
| Paper Maturity | Submission-ready |
| Ethics-Relevant Content | Driving-scene data only; no human-subject data |

**Claimed contributions**: (C1) a learned, content-adaptive token-pruning module for dense prediction; (C2) a token-restoration decoder that recovers full-resolution outputs; (C3) "2.1× faster than the strongest ViT segmenters at comparable accuracy" on ADE20K and Cityscapes.

**Team (fictional personas)**
- **EIC (meta-reviewer)**: Dr. Ilse Marquardt, vision group, large public research university (Europe). Dense prediction; long-time area chair. Reads all five reviews, checks the decisive points, weights the reviewers and decides.
- **R1 (Methodology)**: Dr. Tomás Okafor-Reyes, industrial research lab (North America). Token pruning and merging, latency benchmarking. Insists on measured latency under matched settings.
- **R2 (Domain)**: Prof. Hye-jin Baek, vision lab, public research university (East Asia). Semantic segmentation architectures and benchmarks.
- **R3 (Perspective)**: Dr. Arjun Venkataraman, embedded-systems group, technical university (South Asia). Hardware-aware ML, edge accelerators.
- **R4 (Generalist)**: Dr. Sofia Lindqvist, vision group, mid-size university (Northern Europe). Broad CV background (recognition, video); a typical committee member.
- **Devil's Advocate**: Dr. Noor Haddad, evaluation-methodology group, research institute (Middle East). Benchmarking methodology, confound analysis.

---

## Phase 1: Reports (abbreviated)

### R1 Methodology (Dr. Okafor-Reyes): Overall 3, Confidence 5
- **W1 (comparison fairness)**: Table 2 compares AdaPrune-Seg at 640×640 against the baselines' published 512×512 numbers. *Fix*: rerun the two strongest baselines at 640×640, or report AdaPrune-Seg at 512×512.
- **W2 (latency methodology)**: latency is measured in FP16 for the proposed method; precision for the baselines is not stated (§4.1). *Fix*: state precision, framework and batch size for all rows; add batch-8 and an edge device.
- **W3 (variance)**: the +0.4 mIoU over the pruning-free baseline (Table 3) is a single run. *Fix*: 3 seeds for the Table 3 ablation (≈ 60 GPU-hours).
- **Recomputed**: "2.1×" = 41 ms / 19.6 ms ≈ 2.09× from Table 4. Consistent.

### R2 Domain (Prof. Baek): Overall 4, Confidence 4
- **W1**: Related Work misses token-*merging* approaches adapted to dense prediction, which are the closest competitors. *Fix*: compare with at least one training-free token-merging method on the same backbone.
- **W2**: the restoration decoder resembles existing feature-upsampling decoders; clarify the difference (§3.3).

### R3 Perspective (Dr. Venkataraman): Overall 4, Confidence 3
- Irregular token sets are hard to accelerate on edge NPUs that expect static shapes. *Fix*: one static-shape deployment (fixed keep-ratio buckets) on an embedded device.
- Raises an ethics concern about surveillance use that the paper's driving-scene setting doesn't support.

### R4 Generalist (Dr. Lindqvist): Overall 4, Confidence 4
- **Contribution in one paragraph**: a drop-in pruning module that halves ViT segmentation latency with little accuracy loss. Clear and useful for the CVPR audience.
- **Strengths**: clear motivation and Fig. 2; the trade-off curve (Fig. 5) is the most convincing evidence.
- **Weaknesses**: the abstract's "comparable accuracy" hides that accuracy is only comparable at the higher resolution (Table 2 footnote). *Fix*: state the setting in the abstract.

### Devil's Advocate (Dr. Haddad): Overall 3, Confidence 4
**Steelman**: if content-adaptive pruning preserves accuracy at half the cost, it is a practical win for every ViT segmenter.
**Strongest counter-argument**: the headline claim (C3) rests on Table 2, where the proposed model uses a higher input resolution *and* a longer schedule (160k vs. 80k iterations, Appendix B) than the copied baseline numbers. "Comparable accuracy" may come from these advantages, with pruning actually costing accuracy that they hide.
- **DA-C1 (CRITICAL; resolvable by: new experiments)**: confounded main comparison (Table 2 + Appendix B).
- **DA-M1 (MAJOR)**: small-object accuracy is not reported (per-class IoU missing).
- **DA-m1 (MINOR)**: Fig. 6 qualitative examples are not stated as random.

---

## Phase 2: EIC Meta-Review and Decision

### BEFORE score (prepared by the synthesizer)
Confidence-weighted composite **62.9 → 4 (Borderline Accept)**, with DA-C1 pending the EIC's ruling.

### The case for and against
- **For**: a simple, general module with a clear 2× latency win (Table 4, recomputed by R1), a convincing trade-off curve (Fig. 5) and clear writing (R4, R2).
- **Against**: the headline accuracy parity is measured under settings that favor the proposed method (DA-C1, R1-W1), and the closest competitors (token merging) are not compared (R2-W1).

### Verification of decisive points (EIC read of the paper)
| Point | Raised by | Location | EIC finding | Note |
|-------|-----------|----------|-------------|------|
| Resolution/schedule confound in the main table | DA-C1, R1-W1 | Table 2, App. B | **Verified** | Real, but Table 3 compares against the paper's own pruning-free baseline at matched settings (−0.4 mIoU at 1.9× speed), so the pruning effect *is* partly isolated |
| Latency conditions unstated for baselines | R1-W2 | §4.1, Table 4 | Verified | Fixable by clarification |
| Token merging missing | R2-W1 | §2, Table 2 | Verified | Missing comparison |
| Surveillance concern | R3 | — | **Incorrect for this paper** | Driving scenes only; no person-level analysis |

### Reviewer weights
| Reviewer | Overall | Confidence | EIC weight | Reason |
|----------|---------|------------|------------|--------|
| R1 (Methodology) | 3 | 5 | **1.25** | Every point verified; recomputed the headline speedup; decisive for the outcome |
| R2 (Domain) | 4 | 4 | 1.0 | Sound; the closest-competitor gap is real |
| R3 (Perspective) | 4 | 3 | **0.75** | Deployment point useful, but the ethics concern doesn't apply to this paper |
| R4 (Generalist) | 4 | 4 | 1.0 | Well calibrated to CVPR; identified the abstract overclaim |
| DA | 3 | 4 | 1.0 | The confound is real (verified); its severity is addressed by the ruling below |

### DA-CRITICAL ruling
| Issue | AC test: fatal on its own? | Ruling | Resolvable by |
|-------|---------------------------|--------|---------------|
| DA-C1 | **No.** The matched in-paper comparison (Table 3) supports a narrower version of C3. This is a confound "that a matched experiment could resolve", which the strict criteria list as MAJOR | **Downgraded to MAJOR** | New experiments (matched baselines) |

### BEFORE and AFTER scores (output of `scripts/aggregate_scores.py`)

| Reviewer | Confidence | Confidence weight | EIC quality weight | Share of final score |
|---|---|---|---|---|
| R1 (Meth.) | 5 | 1.00 | 1.25 | 29% |
| R2 (Domain) | 4 | 0.85 | 1.00 | 20% |
| R3 (Persp.) | 3 | 0.70 | 0.75 | 12% |
| R4 (Gen.) | 4 | 0.85 | 1.00 | 20% |
| DA | 4 | 0.85 | 1.00 | 20% |

| Dimension | R1 (Meth.) | R2 (Domain) | R3 (Persp.) | R4 (Gen.) | DA | Before (confidence) | After (EIC-weighted) | Spread |
|---|---|---|---|---|---|---|---|---|
| Technical Rigor | 58 | 66 | 70 | 64 | 52 | 61.6 | 61.0 | 18 |
| Clarity & Presentation | 74 | 76 | 80 | 78 | 75 | 76.4 | 76.1 | 6 |
| Novelty & Originality | 60 | 55 | 68 | 62 | 58 | 60.3 | 60.0 | 13 |
| Significance & Impact | 64 | 68 | 74 | 66 | 60 | 66.0 | 65.6 | 14 |
| Experimental Validation | 48 | 60 | 62 | 58 | 42 | 53.5 | 52.8 | 20 |
| Reproducibility | 62 | 66 | 68 | 66 | 64 | 65.0 | 64.7 | 6 |
| Ethical Compliance | 70 | 72 | 58 | 70 | 66 | 67.6 | 68.2 | 14 |
| **Composite** | 60.4 | 65.0 | 68.3 | 65.0 | 57.0 | **62.9** | **62.5** | |

**BEFORE** 62.9 → 4 · **AFTER** 62.5 → 4 · **DA ceiling**: none (DA-C1 downgraded) · **Final (EIC)**: **4, Borderline Accept**

Note that the weighting moved the score *down* slightly: the EIC trusted the stricter, fully verified R1 more and the more lenient R3 less. Weights reflect review quality, not a leniency knob.

### Final decision and justification
**4, Borderline Accept.** The decision follows the AFTER band. The contribution is useful and clearly presented, and the core speedup is verified. The main weakness is a real but bounded confound in the headline comparison. The paper's own matched ablation supports a narrower claim, so this is the kind of weakness accepted CVPR papers commonly have, provided the rebuttal adds matched baselines and the abstract is reworded.

### Cross-Venue Outlook (user asked "compare venues")

| Venue | Venue-weighted composite | Bar offset | Band → with DA cap | Venue recommendation | Venue sub-scores | Scale status |
|---|---|---|---|---|---|---|
| CVPR (2026) | 61.8 | +0 | 4 → 4 | 4 Borderline Accept | — | confirmed |
| ICLR (2026) | 62.5 | +0 | 4 → 4 | 6 on {0,2,4,6,8,10} (6 on {1,3,5,6,8,10}) | Soundness 2, Presentation 3, Contribution 2 | secondary |
| ICML (2025) | 62.1 | +0 | 4 → 4 | 3 Weak accept (leaning accept) | — | official |
| ACM Multimedia (2026) | 62.5 | +0 | 4 → 4 | Weak accept | — | unpublished |
| TMLR (2025) | 62.2 | -5 | 4 → 4 | Accept with minor revision | Claims & evidence Yes, Audience interest Yes | official |
| IEEE TPAMI (2025) | 62.0 | +3 | 3 → 3 | Major Revision | — | secondary |

**EIC's venue advice**: CVPR is the natural fit. TMLR would accept the paper with a narrowed C3, since it doesn't penalize modest gains. ACM MM would need a multimedia angle to pass its scope gate. TPAMI's higher bar would require the edge-device study and broader backbones.

### Revision Roadmap (Priority 1)

| # | Issue | Source IDs | Location | Fix | Effort | Rebuttal-feasible? |
|---|-------|-----------|----------|-----|--------|--------------------|
| R1 | Confounded headline comparison (resolution, schedule) | DA-C1 (→ MAJOR), R1-W1 | Table 2, App. B | Matched 512² / 80k comparison vs. the 2 strongest baselines; reword C3 | High (~150 GPU-h) | Partially (one baseline) |
| R2 | Latency conditions unstated | R1-W2 | Table 4, §4.1 | Same precision/framework/batch for all rows | Low | Yes |

**Priority 2**: token-merging comparison (R2-W1); per-class IoU / small objects (DA-M1); 3-seed ablation (R1-W3); edge-device deployment (R3); decoder novelty (R2-W2); abstract wording (R4).
**Priority 3**: random qualitative samples (DA-m1).
