# External benchmarks: notes

Notes on outside benchmarks for evaluating AI reviewers, and how each could plug into this repo.
These are notes only; none of them is wired into the evaluation tools yet.

## CSPaper benchmark (cspaper.org/benchmark)

- Score-prediction leaderboard per venue. Metrics:
  - NMAE = mean |S_gt − S_pred| / (S_max − S_min) (lower is better);
  - NME = the signed version (0 is unbiased);
  - SRC = Spearman;
  - AWC = average word count.
  - Reported ± std across papers; the number of papers per venue is not stated.
- Reference: Claude Sonnet 5.5 on ICLR main, NMAE 0.128, NME −0.015, SRC 0.658.
  Not directly comparable with our pilots (unknown N, possible paper overlap with training data).
- Status: NMAE/NME are implemented in `evals/iclr_calibration.py` (`evaluate` and `pilot`);
  pilot results are in `REPORT_iclr2026_pilots.md`.

## CoCoReviewBench (arXiv 2605.07905, github.com/hexuandeng/CoCoReviewBench)

- **What it measures**: review *content*, not scores. An LLM judge (GPT-5-Mini by default) scores
  each review category 1–5 for:
  - Correctness, Thoroughness, Grounding, Verifiability, Clarity;
  - plus category completeness (Complete).
- **How the references are built**: human reviews are filtered for correctness using
  reviewer–reviewer and reviewer–author conflicts, with the meta-review as context. A category is
  scored only where human references exist. The human baseline is leave-one-out.
- **Data**: 3,900 papers, 300 per year, stratified by score:
  - ICLR 2017–2025 and NeurIPS 2021–2024.
  - Each paper has paper Markdown, human reviews with sub-scores and Overall, the meta-review,
    the decision, and atomic opinions with category and correctness labels.
- **License**: CC BY 4.0 (data and code).
- **AI review input**: JSONL lines of `{"id", "text"}`, which is easy to export from our runs.
- **Pipeline requirements**:
  - split/classify use their Qwen3-8B models (ReviewSplit, ReviewClassify) served with vLLM on GPUs;
  - the judge is an OpenAI-compatible API;
  - dependencies are vllm, transformers, bert-score and others.
  
  So it must run outside this repo's stdlib tools and outside the current GitHub Actions jobs (no GPU).
- **Caveats**:
  - The paper Markdown is not blinded (author names and affiliations come first); it would need
    our normalization before going to reviewer agents.
  - Every year predates current model training cutoffs; ICLR 2025 has 210/300 arXiv versions.
    Expect recognized papers, and report them separately.
  - Decisions are not at natural rates because sampling is stratified by score
    (ICLR 2025: 161 Reject, 139 Accept).
- **Possible plan, not started**:
  - A. A stdlib adapter: sample ICLR 2025, blind the Markdown, run the existing review workflow,
    export `{"id","text"}`, and compute NMAE/NME/Spearman/AUC against the human Overall
    (legacy 1–10 scale, `--year 2025`). A 20-paper Sonnet high-effort pilot would cost about $35–40.
  - B. Content scoring with their pipeline. It needs a GPU and an OpenAI key; with a Claude judge
    the numbers are internal only.

## IntelLabs AI-Peer-Review-Detection-Benchmark (Hugging Face)

- **What it is**: about 789k paired human and AI reviews, built for *detecting* AI-written reviews,
  not for judging review quality or score accuracy.
- **Coverage**: ICLR 2017–2024 and NeurIPS 2016–2024. AI reviews come from GPT-4o,
  Claude 3.5 Sonnet, Gemini 1.5 Pro, Llama 3.1 70B and Qwen 2.5 72B.
- **License**: Intel OBL internal R&D use. The dataset card lists "training language models to
  mimic peer review quality" as out of scope.
- **Decision**: not used. The task is different, the license is restrictive, and the models and
  years are old.

## Open-weight reviewer models (candidate baselines)

DeepReviewer, CycleReviewer, OpenReviewer and SEA-E are fine-tuned reviewer models. Benchmarks
such as Re² and CoCoReviewBench use them as baselines.

| | DeepReviewer | CycleReviewer | OpenReviewer | SEA-E |
|---|---|---|---|---|
| Source | ACL 2025, arXiv 2503.08569 | ICLR 2025, arXiv 2411.00816 | NAACL 2025 demo, arXiv 2412.11948 | EMNLP 2024, arXiv 2407.12857 |
| Weights (Hugging Face) | `WestlakeNLP/DeepReviewer-7B` (Qwen2.5), `-14B` (Phi-4) | `WestlakeNLP/CycleReviewer-ML-Llama-3.1-8B`, `-Llama-3.1-70B`, `-ML-123B` | `maxidl/Llama-OpenReviewer-8B` | `ECNU-SEA/SEA-E` (Mistral-7B) |
| License | other (terms to accept) | see model cards | Llama 3.1 | tagged Apache-2.0; card says no commercial use |
| Training data | DeepReview-13K, synthetic stepwise reviews (ICLR 2024–2025) | Review-5k (ICLR 2024) | about 79k ML conference reviews | reviews from 8 venues, standardized by SEA-S |
| Method | multi-stage reasoning (Fast / Standard / Best modes) | several simulated reviewers plus a senior reviewer, scores averaged | one pass over the review form | review, then a consistency check (SEA-A "mismatch score") and regeneration |

Reported numbers are the authors' own and are not comparable with our pilots: the paper sets,
sizes and targets all differ.

- **DeepReview Table 2.** Columns are ICLR 2024 / ICLR 2025; rating is on 1–10 against the
  mean human rating.

  | Model | Spearman | Rating MAE | Decision acc. |
  |---|---|---|---|
  | DeepReviewer-14B | 0.356 / 0.405 | 0.91 / 0.92 | 0.64 / 0.69 |
  | CycleReviewer-70B | 0.336 / 0.267 | 1.25 / 1.21 | 0.63 / 0.68 |
  | CycleReviewer-8B | 0.280 / 0.279 | 1.24 / 1.21 | 0.64 / 0.68 |
  | DeepSeek-R1 | 0.326 / 0.324 | 1.65 / 1.81 | 0.52 / 0.43 |
  | Claude 3.5 Sonnet | 0.037 / −0.022 | 1.50 / 1.35 | 0.48 / 0.56 |

  The last two rows are single-prompt reviewers in the AI Scientist style.
- **OpenReviewer.** On 400 papers its ratings follow the human distribution, while GPT-4 and
  Claude 3.5 rate too leniently.
- **Other evaluations.** arXiv 2604.19502 measures MAE 0.86 for OpenReviewer-8B and 1.10 for
  SEA-E under its own setup. NAIPv2 (arXiv 2509.25179) could not reproduce the four models and
  quotes the published numbers instead.
- **CoCoReviewBench (content).** DeepReviewer-14B scores at about the Qwen3-32B level, below
  GPT-5 and Gemini-3.

**Relevance to us**

- All four were trained on data up to ICLR 2024–2025, so ICLR 2026 is unseen by them. That makes
  them fair open-weight baselines on our ICLR 2026 sample.
- Running them needs a GPU: about 24–48 GB for the 7–14B models and several GPUs for the 70B
  model. They also need an input adapter (Markdown or extracted PDF text). The current
  GitHub Actions jobs have no GPU.
- Our Sonnet pilot (Spearman 0.48, n = 20, CI 0.09–0.74) is in the same range as
  DeepReviewer-14B's 0.405. Only a run on the same papers can say which is better.
- Ideas worth reusing:
  - SEA-A's review–paper mismatch score as an extra grounding metric;
  - DeepReviewer's evidence that more reasoning improves ranking, consistent with our
    high-effort result.

**Possible plan, not started**: run DeepReviewer-14B and CycleReviewer-8B (and optionally
OpenReviewer-8B and SEA-E) on the same 20, later 86, ICLR 2026 papers, using the same blinded
text. Score them with `iclr_calibration.py pilot` and `evaluate`.
