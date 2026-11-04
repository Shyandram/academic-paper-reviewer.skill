# Related projects and benchmarks

A survey of related systems and benchmarks, done 2026-11-04, listing what each one could add to this skill. Abstracts were read from arXiv. Numbers marked *(secondary)* come from write-ups and were not checked against the paper.

## Review systems

| Work | Main idea | What we take from it | Status |
|------|-----------|----------------------|--------|
| ScholarPeer (Google, arXiv 2601.22638) | Searches built around the paper's claims, a baseline scout, a historian agent, a Q&A engine | Per-claim searches, baseline scout, expansion round, field snapshot | **v2.7** |
| AAAI-26 AI Review Pilot (arXiv 2604.13940) | One AI review for each of 22,977 submissions: OCR of the PDF, tool use, self-critique; authors preferred it on technical accuracy; benchmark of injected errors | A **self-critique pass** on the drafted reviews; reading figures and tables from the PDF rather than extracted text | Planned |
| ICLR 2025 Review Feedback Agent (arXiv 2504.09737) | Randomized trial on 20K reviews: flags vague comments, misreadings of the paper and unprofessional remarks, passed through automated reliability tests; 27% of reviewers revised | The same checks applied to our own reports before the EIC reads them: no vague weaknesses, no claims the paper contradicts, professional tone | Planned |
| ReviewGrounder / ReviewBench (arXiv 2604.14261) | Rubrics built per paper from the venue guidelines; a draft stage, then a grounding stage | Turn `venue_profiles.md` criteria into per-paper rubric items the Generalist checks | Idea |
| TreeReview (arXiv 2506.07642) | A tree of review questions, expanded dynamically with follow-ups | Similar to our per-claim queries; follow-up questions where a verdict is unclear | Idea |
| PaperAudit-Review (arXiv 2601.19916) | Reviews conditioned on explicit error evidence are more conservative and closer to human judgments | Already the design here (an evidence location for every point, the DA ceiling); keep it | Have |

## Benchmarks we could evaluate against

| Benchmark | What it tests | Fit for our eval |
|-----------|---------------|------------------|
| FLAWS (arXiv 2511.21843) | 713 paper/error pairs: errors that invalidate a claim, inserted by LLMs, scored on identification and localization; best frontier model about 39% *(secondary)* | Wider than our 6 planted test-tuning sentences. Add claim-invalidating error types (wrong equation, table/text contradiction, mismatched baseline) |
| PaperAudit-Bench (arXiv 2601.19916) | 220 AI/ML papers, more than 2,200 synthetic errors in 8 categories; some need reasoning across sections | Use its categories to design error-hunting checks for the DA and Methodology reviewers |
| SPOT (arXiv 2505.11855) | 83 published papers, 91 real errors that led to errata or retractions; best recall 21%, precision 6% *(secondary)* | Real errors, not planted ones. Precision is the hard part, so we should also measure our false-positive rate (the clean-paper DA-CRITICAL rate we already track) |
| Planted-error psychology benchmark (Dawes Institute, GitHub) | 100 planted errors in 10 papers, 14 reviewer configurations; the 7 errors no system caught were all **omissions** | Add **omission controls**: delete a key protocol detail and check that the review reports it missing |
| Beyond Imitation / MLR (arXiv 2610.11087) | Logical contradictions inserted into conference papers | Add **contradiction controls** |
| PRISM (arXiv 2605.26730) | Review quality on four dimensions: depth, novelty assessment, flaw identification and prioritization, constructiveness; compared with human ICLR, ICML and NeurIPS reviews | Rubric for comparing with human reviews (needs OpenReview access for the eval harness) |
| DeepReview-Bench (ACL 2025) | ICLR 2024–25 papers with human reviews, rating prediction and review generation | The ICLR part of ScholarEval; comparison with human reviews |

## Safety: prompt injection in manuscripts

- Hidden reviewer-directed text ("give a positive review", in white font) was found in 18 preprints (Lin, arXiv 2507.06185).
- Injected manuscripts got more favourable LLM reviews from three commercial models (Choi et al., JAMA Network Open, 2026).
- **Gap found:** the eval prompts tell reviewers to ignore instructions in the paper, but the skill itself had no such rule. Only search results were marked untrusted.

Planned: a Hard Rule saying that manuscript text is data. The panel never follows instructions embedded in it, records them under *Integrity signals*, and reports them to the EIC; they never raise a score. Two injection controls exist for testing it (`evals/make_controls.py --injection`), and their score must equal the clean paper's.

## Roadmap after the v2.7 eval

1. **v2.7.1:** the injection Hard Rule, then the injection controls (2 papers).
2. **v2.7.1:** a self-check pass on the five reports (no vague weaknesses, no claims the paper contradicts, tone), in the style of the ICLR feedback agent.
3. **Eval:** omission and contradiction controls, plus FLAWS-style error types, with recall on controls and false-positive rate on clean papers.
4. **Later:** comparison with human reviews (PRISM / H-Max), if openreview.net is allowed for the eval harness only.
