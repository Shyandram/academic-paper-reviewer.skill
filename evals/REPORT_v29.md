# v2.9 evaluation: claim-level novelty profile

Two runs on Haiku with the strict literature check.

| Run | Final | Novelty profile (as written) | After the label fix (recomputed) | Notes |
|---|---|---|---|---|
| iclr-detseg (lit29) | 4 | C1 high, C2 not found, C3 high, C4 high | C1 **medium**, C2 **medium**, C3 high, C4 high | The λ/τ/θ selection on LVIS minival is MAJOR via field practice. No central claim is fully covered. |
| eccv-vlm (lit29) | 3 | C1–C3 medium | unchanged | DA-C1 upheld (test-set selection), consistent with lit28 |

- **Bug found:** `novelty` ignored the arXiv-only prior label (`prior (arXiv-only, 6+ months before the cutoff)`) because it expected a shorter string. It is fixed, with a test that reads the labels from the filter.
- **Workflow:** both runs wrote `novelty_profile.json` and `novelty.json` and reported the paper reading. Neither treated one partially covered claim as a reason to reject.
- **Wording:** criterion 3 now says the field-practice case is a validation split with public labels, reported because the test labels are hidden.
