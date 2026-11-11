# Error Audit

A structured hunt for concrete errors: specific, located mistakes that weaken a claim, as distinct from general weaknesses. It runs inside Phase 1. The Methodology Reviewer runs the main audit, the Domain Reviewer checks citations, the Devil's Advocate checks claim distortion and re-checks the top claims, and the EIC rules on what survives.

Why this exists: on error-detection benchmarks, LLM reviewers find a minority of the errors they are tested on, and many of the errors they report are not real. On SPOT (arXiv 2505.11855; real errata and retractions), the best model reached 21% recall and 6% precision. On FLAWS (arXiv 2511.21843; errors that invalidate a claim), the best model identified 39% of errors when allowed 10 guesses. On PaperAudit-Bench (arXiv 2601.19916), reading section by section with a shared summary of the paper (the "paper memory") detected more errors than single-pass reading, especially inconsistencies between sections. Claim distortion and rhetorical overclaiming were the hardest categories to detect. On a planted-error benchmark (Dawes Institute), every error that no system caught was an **omission**. This procedure targets those failure modes, and its precision rules target the false positives.

---

## 1. Categories

| # | Category | What to look for | Typical check |
|---|----------|------------------|---------------|
| E1 | **Result inconsistency** | The same quantity differs between the abstract, text, tables and figures. A stated gain doesn't match the table. An average doesn't match its rows. Units or scales are wrong. | Recompute deltas, means and percentages from the table; compare every headline number with its source table |
| E2 | **Equation, proof or algorithm error** | A wrong derivation step, sign or index. Dimensions or units that don't match. An algorithm that doesn't implement the equation. A term counted twice. | Check the key steps; with a code tool, test small numeric cases |
| E3 | **Assumption error** | An assumption that is unstated, contradicted by the setup, or violated by the experiments. A theorem applied outside its conditions. | List the assumptions behind each main claim; check each against the setup |
| E4 | **Protocol flaw** | Leakage, selection on the test set, unequal baselines (data, backbone, schedule, resolution), ablations that don't isolate the component, inconsistent evaluation settings | Protocol Sweep (Methodology Step 0); fairness audit |
| E5 | **Claim distortion** | A conclusion that goes beyond the evidence, unqualified superlatives ("first", "state of the art", "consistently", "always"), a mechanism asserted but never tested | Claim-by-claim check (Section 2); the hardest category, so check it explicitly |
| E6 | **Definition or setup inconsistency** | A symbol, dataset, split, hyperparameter or model size defined differently in two places. The method in the text differs from the one in the figure or appendix. | Build the paper memory (Section 3) and compare across sections |
| E7 | **Citation error** | A cited work doesn't support the claim attributed to it. The wrong paper sits behind a name (e.g., the text cites method A, the bibliography entry is method B). Prior work is misrepresented. | Domain Reviewer: compare the citation context with the bibliography entry and, if a literature check ran, the kept abstract |
| E8 | **Omission** | Something a result depends on is missing: split and tuning protocol, seeds and variance, compute, baseline settings, data licence or consent, failure cases, limitations | Omission sweep (Section 4) |
| E9 | **Figure or table integrity** | Duplicated or reused panels, a caption that contradicts its content, axes or legends that don't match the text. Only with page images. | Read the figures as images; without images, say this was not checked |

Use E9 only when you can see the figures. Never infer duplication from extracted text.

---

## 2. Claim-grounded audit

Errors that matter break a **key claim** (this is how FLAWS defines them). For each contribution claim C1, C2, … (from the Methodology Reviewer's claim-to-evidence map):

1. **What must be true** for the claim to hold? List 2–4 conditions: the experiment exists, the comparison is fair, the numbers match, the derivation is correct, the assumptions hold, the wording matches the evidence.
2. **Check each condition** against the paper memory and the text, at the cited locations.
3. Record any condition that fails as an error (Section 5). Record a condition you could not check (a figure was unavailable, an equation was garbled in extraction) as **unverifiable**. That is a note, never an error.

---

## 3. Paper memory (Phase 0, shared with all reviewers)

A short factual record, built once in Phase 0. It is a description, not a judgment, so sharing it doesn't break reviewer independence. It follows the three-pass reading in Beyond Imitation (arXiv 2610.11087) and PaperAudit's global memory.

- **Claims:** C1, C2, … quoted or closely paraphrased, with locations. Mark one as **primary**: the contribution the abstract leads with (when it lists several, the first). It is fixed here, before any search; every reviewer, the novelty profile and the EIC use this one.
- **Setup facts:** datasets and splits (train / validation / test as named), backbone and pretraining, resolution, schedule, compute, seeds. Each with its location, or "not stated".
- **Headline numbers:** each number in the abstract and introduction, with its source table or figure.
- **Appendix and supplement summary:** what they add: extra experiments, implementation details, protocol statements. A reviewer must not raise a weakness that the appendix already answers.
- **Unverifiable parts:** figures not available, garbled equations or tables.

---

## 4. Omission sweep

LLM reviewers miss omissions because there is no sentence to react to. For each item, search the full text, appendix and supplement included (use text search), and write **present (location)** or **not stated after search**:

| Item | Needed when |
|------|-------------|
| Train / validation / test split, and which split was used for tuning and selection | Always, for empirical papers |
| Seeds, number of runs, variance | Any claim of improvement |
| Baseline settings (official code or reimplementation; same data, backbone, schedule) | Any comparison |
| Hyperparameters and how they were chosen | Always |
| Compute (hardware, time) | Efficiency claims; reproducibility |
| Dataset licence, consent, personal data | New data, human subjects, faces, medical data |
| Failure cases and limitations | Always |
| Code or data availability | Reproducibility claims |

A missing item is an error (E8) only if a claim depends on it. Otherwise it is a reproducibility note.

---

## 5. Error log and precision rules

Each error goes into the reviewer's **Error Log** (in the report's Weaknesses section or an appendix to it):

| ID | Category | Location | Verbatim quote (≤ 25 words) | Why it is an error | How verified | Confidence | Minimal repair → claim survives? | Severity | Fix |
|----|----------|----------|-----------------------------|--------------------|--------------|------------|----------------------------------|----------|-----|
| ERR-1 | E1 | Table 2 vs. §4.2 | "improves mAP by 3.1" | Table 2 gives 47.9 − 45.6 = 2.3 | Recomputed | High | Correct the number → intact (gain still holds), but the headline number changes | MAJOR | Correct the text or the table |

Precision rules (false alarms cost the authors' and the editor's time, and erode trust):
- **No quote and no location, no error.** If you cannot point to the text, it goes under Questions.
- **"How verified" must be concrete:** recomputed, cross-referenced (two locations given), derived, or checked against a cited source. "Seems wrong" is not verification.
- **Confidence.** High: verified directly. Medium: verified, but depends on an interpretation. Low: suspected. **Low-confidence items go under Questions, never under Weaknesses.**
- **Extraction artifacts are not errors.** Garbled equations, merged table cells and broken symbols from PDF extraction are "unverifiable", not mistakes by the authors.
- **Check the appendix first.** An "omission" answered in the appendix is not an error.
- **Rank, don't pile up.** List errors by severity. Put cosmetic slips (typos, formatting) in one line under Minor; never inflate them into weaknesses.

---

## 6. Severity and the decision

**Repair test.** For every error you would rate MAJOR or CRITICAL, add two fields to its Error Log entry before rating it: the **minimal repair** (what would change: an added assumption, a corrected constant, a restricted statement, a rerun, a new experiment) and whether the affected claim **survives** that repair: *intact*, *weakened* (holds in a narrower form) or *lost*. Severity follows the answer:

- **Lost**, or leakage, fabrication or an ethical violation: CRITICAL candidate, under the strict DA-CRITICAL criteria (`agents/devils_advocate_reviewer_agent.md`).
- **Weakened**, or a headline number changes but not the conclusion, or a missing disclosure a claim depends on: MAJOR.
- **Intact** after a local fix (a wrong derivation step with the result intact, a typo in a bound, a missing regularity condition the authors can add): MAJOR only if the repair needs new work (a new proof step, a rerun), otherwise MINOR.
- Everything else is MINOR.

**Counting and scoring.** Errors in one proof, derivation or experiment chain are **one issue**, rated by its worst consequence. The number of errors never sets a score. A repairable gap in a proof is common in accepted theory papers: unless the claim is lost or weakened, it lowers Technical Rigor by at most one pool band, and it does not move the pool position on its own. Ask the calibration question: *would an accepted paper at this venue plausibly carry this gap to the camera-ready version?*

The EIC verifies every MAJOR and CRITICAL error at its location in Phase 2, including the repair test, before it counts.
