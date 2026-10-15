# Computer Vision & ML Review Checklist

Task-specific checks for CV, ML and multimodal papers, for the Methodology and Domain reviewers. Benchmarks and metrics evolve; treat the lists below as the *minimum* expected and ask for the field's current standard when you are unsure.

---

## 1. Universal CV/ML Confounds

Ask about each of these whenever a paper claims to beat prior work:

| Confound | What to ask |
|----------|-------------|
| Backbone | Same backbone (and size) as the baselines? If not, is there a matched-backbone row? |
| Pretraining data | ImageNet-1k vs. 22k vs. web-scale (CLIP/LAION-style) vs. in-house data? Self-supervised vs. supervised initialization? |
| Input resolution | Same train and test resolution? Higher resolution alone often adds points. |
| Training schedule | Same epochs/iterations? Long schedules inflate gains. |
| Augmentation & regularization | Stronger augmentation (e.g., large-scale jitter, Mixup/CutMix) applied only to the proposed method? |
| Test-time tricks | TTA, multi-scale, flipping, sliding window, ensembling: applied consistently? |
| Extra data / labels | Pseudo-labels, extra datasets, additional annotation types? |
| Baseline numbers | Copied from the papers (different settings?) or reproduced (tuned equally?)? |
| Hyperparameter selection | Tuned on validation or on test? Same tuning budget for baselines? |
| Compute | Same GPU budget? Report params, FLOPs *and* measured latency. |

## 2. Task-Specific Expectations

### Image Classification / Representation Learning
- Benchmarks: ImageNet-1k (val) plus robustness/OOD variants (e.g., ImageNet-V2/-R/-A/-Sketch) when robustness or generality is claimed; transfer to downstream tasks for representation-learning claims.
- Protocols: linear probe, k-NN and fine-tuning reported separately. Pretraining data and epochs matched in SSL comparisons.
- Report: top-1 (top-5 optional), params, FLOPs, throughput.

### Object Detection & Instance Segmentation
- Benchmarks: COCO (val and/or test-dev; say which), LVIS for long-tail, plus a domain-specific set if relevant.
- Metrics: AP, AP50, AP75, APs/APm/APl; AP^mask for instance segmentation; APr for LVIS.
- Watch for: test-dev vs. val confusion, larger backbones hidden in "ours", schedule mismatch (1× vs. 3×), and Objects365 or other extra pretraining.

### Semantic / Panoptic Segmentation
- Benchmarks: ADE20K, Cityscapes, COCO-Stuff/Panoptic, Pascal Context; medical datasets for the medical domain.
- Metrics: mIoU (single-scale *and* multi-scale, clearly labeled), PQ/SQ/RQ for panoptic; Dice/HD95 in medical imaging.
- Watch for: single-scale vs. multi-scale mixed in one table; crop-size differences.

### Video Understanding / Tracking
- Benchmarks: Kinetics, Something-Something v2 (temporal reasoning), MOT17/20, DanceTrack, YouTube-VOS/DAVIS.
- Metrics: top-1 with views × crops stated; HOTA, IDF1, MOTA for tracking; J&F for VOS.
- Watch for: frame-sampling differences, inference views not matched, detectors trained on extra data in tracking.

### 3D Vision, NeRF, Gaussian Splatting
- Benchmarks: standard scene sets (e.g., synthetic Blender scenes, Mip-NeRF 360, Tanks & Temples, LLFF, DTU); ScanNet/KITTI/nuScenes for 3D perception.
- Metrics: PSNR/SSIM/LPIPS on held-out views (the benchmark's split), Chamfer distance / F-score for geometry; training time, FPS, memory and model size.
- Watch for: non-standard train/test view splits, per-scene hyperparameters, LPIPS backbone (AlexNet vs. VGG) not stated, camera poses from privileged sources.

### Depth / Optical Flow / Stereo
- Benchmarks: KITTI, NYUv2, Sintel, Middlebury, ETH3D.
- Metrics: AbsRel, δ<1.25 for depth; EPE and Fl-all for flow; bad-pixel rates for stereo.
- Watch for: scale/shift alignment for monocular depth (state the alignment); training on the benchmark's own training split vs. zero-shot.

### Low-Level Vision / Image Restoration / Super-Resolution
- Benchmarks: Set5/Set14/BSD100/Urban100/Manga109 (SR), standard denoising, deblurring and deraining sets, real-world degradation sets.
- Metrics: PSNR/SSIM (state RGB vs. Y-channel and border cropping), LPIPS/DISTS/NIQE for perceptual claims, and a user study for perceptual-quality claims.
- Watch for: Y-channel vs. RGB mixed across rows; self-ensemble (×8 TTA) results compared against plain baselines; synthetic-only evaluation when "real-world" is claimed.

### Image / Video Generation
- Metrics: FID with the sample count and reference statistics stated (e.g., 50k samples), plus a precision/recall or diversity measure; CLIP score or VQA-based alignment for text-to-image; FVD for video; human preference studies with protocol details.
- Watch for: FID computed with different implementations or resolutions; cherry-picked samples without a random-sample grid; no guidance-scale sweep (trade-off curves); training-data memorization and attribution.
- Ethics: deepfake/misuse potential, consent and licensing of training data, provenance/watermarking.

### Vision–Language Models / Multimodal LLMs
- Benchmarks: a mix of perception, reasoning and hallucination benchmarks; held-out or post-cutoff sets when contamination is possible.
- Report: model versions, prompts, decoding settings, number of samples, and whether answers are parsed by rules or by an LLM judge.
- Watch for: test sets present in instruction-tuning data; prompt engineering on the test set; comparing against closed models at different dates; LLM-as-judge without human validation.

### Medical Imaging
- Patient-level splits (never image-level); external validation on another site or scanner; clinically relevant metrics (sensitivity at fixed specificity, AUC with CIs, Dice/HD95); comparison with clinicians or clinical baselines.
- Watch for: leakage across slices or visits of the same patient; class prevalence differing from clinical reality; no calibration analysis.

### Efficient Models / Compression / Edge Deployment
- Report: params, FLOPs/MACs (say which), **measured** latency with hardware, batch size, precision, resolution and framework; memory; energy if claimed.
- Watch for: FLOPs used as a proxy for speed (token pruning or sparse operations may not speed up real hardware); latency measured with different batch sizes; INT8 vs. FP16 mismatch.

### Remote Sensing, Robotics, Autonomous Driving
- Geographic and temporal splits (no leakage across tiles or time); closed-loop vs. open-loop evaluation for driving and planning; sim-to-real gap.

## 3. Qualitative Evidence

- [ ] Same inputs, crops and zoom for every compared method
- [ ] Selection procedure stated (random seeds or indices vs. curated)
- [ ] Failure cases shown and discussed
- [ ] Attention/saliency visualizations not over-interpreted as explanations
- [ ] No signs of duplicated or manipulated panels (report factually if suspected)

## 4. Datasets Introduced by the Paper

- [ ] Datasheet-style documentation (motivation, composition, collection, preprocessing, uses, distribution, maintenance)
- [ ] License; consent for identifiable people; PII handling; takedown process
- [ ] Annotation protocol, annotator training and pay, inter-annotator agreement
- [ ] Demographic and geographic coverage; bias analysis
- [ ] Standard splits defined and fixed; baseline results provided

## 5. Typical Severity in CV Reviews

| Finding | Typical severity |
|---------|-----------------|
| Headline gain disappears or is unverified once confounds are matched (backbone/pretraining/resolution) | MAJOR → CRITICAL if it is the main claim |
| Evaluation on the wrong split, test-set tuning, or leakage | CRITICAL |
| Missing the strongest recent baseline in the sub-area | MAJOR |
| Efficiency claim without measured latency | MAJOR (if efficiency is a main claim), else MINOR |
| Single run, gain within known noise | MAJOR |
| Single run, large gain on a large benchmark | MINOR |
| Qualitative results curated without disclosure | MINOR–MAJOR |
| No failure cases | MINOR |
