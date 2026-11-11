# Design: skill 2.13, novelty and severity calibration

Status: withdrawn in 2.16 (see CHANGELOG). implemented, not yet evaluated. First committed as 2.10.2; renumbered 2.13 because "2.12" was the working name of what shipped as 2.10.1. Target: GPT-6.1 Sol and Terra (via Codex) without
hurting Sonnet.

## 1. Problem

On pilot 3's 20 ICLR 2026 papers, GPT-6.1 Sol's panel rating does not rank the papers
(Spearman +0.02 against Sonnet's +0.48; paired difference 0.46 [0.08, 0.81]). The diagnosis
(`evals/REPORT_iclr2026_pilots.md`, "Why Sol does not rank the papers") found:

- Sol's reviewers' pool tracks Technical Rigor (0.94), which does not track the humans (+0.04);
  Sonnet's tracks Novelty (0.92), which does (+0.56).
- **Lenient where the problem is novelty.** On four of the humans' weakest papers Sol's pool is
  12–16 points above Sonnet's. None of its top concerns on any paper names a prior work (Sonnet:
  6 of 20 papers). It searches as much as Terra and more than Sonnet.
- **Harsh where a proof flaw is checkable.** A theory paper the humans rated 5.0 is Sol's 19th of
  20 (rigor 38.5, ICLR 2) after it logged a series of proof errors as verified; Sonnet found the
  same main defect and gave ICLR 4.
- Sol reasons about a third as much per paper as Sonnet (9.3k against 30.2k reasoning tokens).

The pattern is defensive: Sol states hard what it can check and softens what it cannot prove.

## 2. What the literature says

- **LLM reviewers under-criticize novelty.** Across 8 LLMs (4 GPT, 2 Llama, 2 DeepSeek) on 676
  OpenReview papers, models praised novelty in strengths but rarely criticized it in weaknesses,
  focusing on technical validity, while human experts spread their weaknesses over validity,
  novelty and clarity; the pattern held regardless of model size or reasoning
  (Shin et al., "Mind the Blind Spots", arXiv 2502.17086). The Stanford Agentic Reviewer cites
  the same gap and Liang et al.'s finding that GPT-4 feedback comments on novelty far less often
  than humans (paperreview.ai/tech-overview).
- **Novelty judgments need named prior work and a facet comparison.** OpenNovelty (arXiv
  2601.01576) compares each contribution claim with each retrieved paper and outputs
  can_refute / cannot_refute / unclear, with verbatim evidence required for can_refute. The Idea
  Novelty Checker (Shahid et al., arXiv 2506.22026) defines novelty by facets: an idea is novel if
  it differs from every retrieved paper in at least one core facet (purpose, mechanism,
  evaluation); expert agreement rose (kappa 0.64 → 0.68) when judgments were tied to the
  retrieved papers, and facet-based re-ranking was the component that mattered most.
- **Severity calibration, not detection, is often the binding constraint.** A concern-level
  study grades fatal / major / moderate / minor and finds detection alone does not decide review
  quality (arXiv 2604.19998); PRISM separates flaws that need new experiments or proof revisions
  from ones fixable by text edits (arXiv 2605.26730). Inflating minor or community-standard
  issues is a listed failure mode of AI reviewers (arXiv 2605.20668).
- **Recent GPT models abstain more and follow instructions literally.** OpenAI reports that
  gpt-5-thinking-mini abstained on 52% of SimpleQA items against 1% for o4-mini ("Why language
  models hallucinate"). The GPT-5 and 5.1 prompting guides say the models follow instructions
  closely, that conflicting instructions are the first thing to check when behaviour is off,
  that GPT-5.1 "can sometimes err on the side of being excessively concise", and that
  persistence and completeness should be asked for explicitly; higher `reasoning_effort` is
  recommended for complex multi-step tasks.

## 3. Where the skill pushes a literal model toward this pattern

Read literally, the 2.10.1 text holds novelty and errors to different standards:

| Rule (2.10.1) | Literal reading | Effect |
|---|---|---|
| Hard Rule 10: suspicions go under Questions, never Weaknesses | A novelty doubt cannot be proven, so it is a suspicion | Novelty doubts become questions |
| Hard Rule 2: recommend a citation only when confident | Do not name a prior work unless sure | No named work in concerns |
| "MAJOR at most" (novelty, 4 places) | Novelty findings may be anything up to MAJOR | They drift to minor |
| ClaimNov paragraph: a strict rule rejected 56.8% of later-published ideas | Avoid calling claims not novel | One-sided caution |
| Level 3 = "partial coverage, important details differ" → verdict "medium" | The safe middle | 83% of Sol's claims topped out at level 3 (Sonnet 62%) |
| EIC departs only for a "verified, named issue" | Errors are verifiable, novelty is not | Only errors move the decision |
| Error severity: a wrong derivation step with the result intact is MAJOR | Every checked defect is at least MAJOR | Repairable proof gaps sink rigor |

Sonnet resolved these conflicts the way human reviewers do; Sol resolved them toward caution.
The OpenAI guidance says to remove such conflicts rather than add more instructions.

## 4. Changes in 2.13

Lessons from 2.11 (withdrawn): new roles and phases cost more and ranked worse. 2.13 adds no
role, phase or agent call. It edits wording and adds one optional field to one script.

1. **Errors and judgments (SKILL.md, Hard Rule 10; `references/error_audit.md`).** Hard Rule 10
   covers errors: statements that something in the paper is wrong. Novelty, significance and
   adequacy of evaluation are judgments. A judgment needs a stated basis (for novelty: a named
   prior work and the facets it shares), not a proof, and a grounded judgment that lowers the
   assessment is a Weakness. Turning it into a question because it cannot be proven understates
   it. This is the precedence rule the conflicting instructions lacked.
2. **Facet-based prior-work levels (`agents/domain_reviewer_agent.md`,
   `references/literature_search.md`, `scripts/related_search.py`).** For each claim and
   candidate prior work, the Domain Reviewer marks which of four facets the prior work shares:
   **problem** (same task or goal), **mechanism** (same core technique), **setting** (same data,
   object or evaluation regime) and **finding** (same result or conclusion). Level = 1 + shared
   facets, so four yes/no decisions replace one holistic 1–5 rating. A prior work sharing problem
   **and** mechanism makes the claim at least "incremental" whatever the count. Each match at
   level 3 or more carries a one-line `delta` (what this paper adds over it). The script accepts
   `shared` alongside or instead of `level`, checks they agree, and warns on a missing delta.
3. **Symmetric novelty guidance.** "MAJOR at most" becomes "MAJOR, not CRITICAL". The ClaimNov
   paragraph keeps its point (a known claim is not a known paper) and gains its other half: when
   every central claim is incremental or known against prior work, that is the "gain over the
   closest prior work is small" signal of a typical rejected submission; write it as a Weakness
   naming the works and place Novelty in the Limited band (30–54) unless the delta shows a gain
   the prior work lacks.
4. **Repair test for errors (`references/error_audit.md` §6, Methodology Reviewer, EIC).** Each
   MAJOR or CRITICAL error states its minimal repair and whether the claim survives it (intact /
   weakened / lost). Severity follows survival. Errors in one derivation chain are one issue; the
   number of errors never sets a score. A repairable gap in a proof is common in accepted theory
   papers: it lowers Technical Rigor by at most one pool band unless the claim is lost.
5. **Two-sided pool position (`references/quality_rubrics.md`, report template).** Before the
   pool position, each reviewer writes the strongest case for acceptance and for rejection in one
   line each, and the deciding factor. The contribution (novelty, significance) sets the
   position; the evidence decides whether the contribution is supported. A defect counts against
   the position when it undercuts the contribution, not because it can be checked.
6. **EIC balance check (`agents/eic_agent.md`).** A grounded novelty judgment counts as a
   verified issue for departing from the starting point. If the reports hold validity issues as
   verified Weaknesses but leave novelty doubts as unnamed Questions, the EIC names the closest
   prior work from the ledger and rules on it, or records that none was found.
7. **Decisive findings in Weaknesses (template).** Every finding that changed a score appears
   under Weaknesses; audit sections may hold the details. (Sol's Weaknesses sections were half
   as long as Sonnet's because it moved findings to audit sections.)
8. **Codex runtime: judgment and persistence (`references/codex_runtime.md`).** Use
   `high` reasoning or above for full reviews (`xhigh` when offered); commit to a value for every
   rating and give a confidence, with "unclear" only when the missing information is named; for
   each central claim whose closest prior work is at level 3 or below, run one more query on its
   mechanism before concluding (within the 12-query budget); and the precedence rule from change 1.

Not changed: the panel, weights, decision rule, DA ceiling, `aggregate_scores.py` and the
eval pipelines.

## 5. Evaluation plan (needs approval: paid API runs)

Same 20 pilot-3 papers, Codex `exec`, 2 in parallel:

| Run | Skill | Effort | Separates |
|---|---|---|---|
| Sol (done) | 2.10.1 | high | baseline |
| Sol A | 2.13 | high | the skill change |
| Sol B | 2.10.1 | xhigh | reasoning effort alone |
| Sonnet | 2.13 | high | no regression on the model that works |

Rough cost: Sol about $1.4–3 per paper (A and B ≈ $60–120 together), Sonnet about $2 per paper
(≈ $40).

Predictions if the diagnosis is right (Sol A against Sol 2.10.1):
- top concerns naming a prior work: from 0/20 papers to ≥ 6/20;
- Novelty's Spearman with the human mean above Sol's +0.19, and Novelty's weight in Sol's own
  pool up from 0.76;
- pool gap between the humans' top and bottom ten from −0.2 to ≥ +3;
- the share of claims topping out at level 3 down from 83%;
- panel-rating Spearman with humans up from +0.02 (with 20 papers, only a large change is
  readable; the paired bootstrap against Sol 2.10.1 is the test).

Sonnet 2.13 should stay within the noise of 2.10.1 (+0.48 [0.12, 0.73]); a paired difference
below −0.2 would mean the changes hurt the model that works and should be split by model.

## 6. Risks

- Harsher novelty on incremental-but-accepted papers. The "Would a typical accepted paper score
  higher?" question and the "MAJOR, not CRITICAL" wording stay; the EIC can still decide above the
  starting point.
- 2.11 also asked Reviewer 2 to name the work (and dropped unnamed weaknesses) and was withdrawn
  after it ranked worse on Sonnet, together with several other changes. Hard Rule 11 drops
  nothing and applies only when a novelty judgment lowers the assessment, but the Sonnet run in
  the plan is there to catch a repeat.
- Facet marking from abstracts misses details; level 4–5 still needs reading beyond the abstract
  before a criterion-7 issue.
- 20 papers can only show large effects; a confirmed gain should be rerun on the 66 other papers
  of the full evaluation.

## Sources

The arXiv papers and the paperreview.ai page were read directly; arXiv 2604.19998, 2605.26730 and
2605.20668 only through search summaries.

- Shin et al., Mind the Blind Spots: A Focus-Level Evaluation Framework for LLM Reviews, arXiv 2502.17086.
- Stanford Agentic Reviewer tech overview, paperreview.ai/tech-overview.
- OpenNovelty, arXiv 2601.01576.
- Shahid et al., Literature-Grounded Novelty Assessment of Scientific Ideas, arXiv 2506.22026 (SDP 2025).
- Concern-level severity study, arXiv 2604.19998; PRISM, arXiv 2605.26730; AI-reviewer failure modes, arXiv 2605.20668.
- OpenAI, Why language models hallucinate (openai.com/index/why-language-models-hallucinate).
- OpenAI cookbook: GPT-5 prompting guide and GPT-5.1 prompting guide (github.com/openai/openai-cookbook, examples/gpt-5).
