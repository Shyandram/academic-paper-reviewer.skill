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
