# Submission Readiness Checklist

Used in `quick` mode and before any submission. In the output, report only the items that fail or are uncertain.

---

## A. Desk-Reject Risks (check first)

- [ ] **Anonymity**: no author names or affiliations; no identifying acknowledgments, grant numbers or URLs; anonymized code links; self-citations in the third person; PDF metadata (Author field) cleared
- [ ] **Page limit**: main text within the limit in the venue's official template, without modified margins or font sizes
- [ ] **Template**: correct year's template, review/anonymous mode enabled (line numbers present where expected)
- [ ] **Required checklists and statements**: paper checklist, reproducibility checklist, ethics or broader-impact statement, LLM-use disclosure: whatever the venue requires
- [ ] **Dual submission**: not substantially overlapping with work under review or published elsewhere
- [ ] **Supplementary material**: within size and format limits; also anonymized

## B. Claims and Evidence

- [ ] Every contribution in the introduction is supported by a specific experiment or proof
- [ ] Abstract numbers match the tables
- [ ] "State-of-the-art", "first", "general" and "robust" claims are scoped to what was tested
- [ ] Limitations section present and honest

## C. Experiments

- [ ] Strongest recent baselines included under matched settings, or differences disclosed
- [ ] Ablation for every claimed component
- [ ] Variance or significance where gains are small (see `references/statistical_reporting_standards.md`)
- [ ] Efficiency claims backed by measured latency with the hardware stated
- [ ] Failure cases shown

## D. Reproducibility

- [ ] Implementation details complete (architecture, optimizer, schedule, batch size, augmentations, loss weights)
- [ ] Hyperparameter selection procedure and tuning split stated
- [ ] Compute resources stated
- [ ] Code/data release plan (anonymized for review)

## E. Presentation

- [ ] Figure 1 conveys the core idea without reading the text
- [ ] All notation defined at first use; consistent symbols
- [ ] Figures legible when printed (font ≥ caption size), colorblind-safe, readable in grayscale
- [ ] Tables have a consistent number of decimals; best results marked as stated
- [ ] Related work positions the paper against its closest competitors, not just a list
- [ ] References complete (venues and years, not only arXiv where a published version exists)
- [ ] Spell-check and grammar pass; no leftover TODOs, comments or "??" references

## F. Ethics

- [ ] Data licenses and consent (especially faces, people, medical data)
- [ ] Misuse potential discussed where relevant (generative models, surveillance)
- [ ] IRB/ethics approval stated for human-subject studies

---

## Readiness Verdict

| Verdict | Criteria |
|---------|----------|
| **Ready** | No failures in A; at most minor items in B–F |
| **Ready after quick fixes (< 1 day)** | No failures in A after easy fixes; B–F gaps are wording, formatting or missing details |
| **Needs substantive work** | Any unsupported main claim, missing key baseline or ablation, or a desk-reject risk that needs more than formatting |
