#!/usr/bin/env python3
"""Create planted-flaw control papers from accepted papers.

Each control is an accepted paper with ONE inserted sentence that admits a
fatal evaluation flaw. A calibrated reviewer must catch it, the EIC must uphold
it as CRITICAL, and the decision must drop to <= 3. This guards against the
calibration fix overcorrecting toward accepting everything.

    python3 evals/make_controls.py evals/manifest.json > evals/manifest_controls.json
"""

import json
import re
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parent / "work" / "papers"

FLAWS = {
    "test-tuning": (
        "All hyperparameters, including the learning rate, loss weights and the "
        "number of training epochs, were selected based on performance on the test set."),
    "train-on-test": (
        "Because the official test split is small, we merged it into the training "
        "set and report all results on the same split."),
}

CONTROLS = [
    ("cvpr-detseg-2604.24119", "test-tuning"),
    ("cvpr-lowlevel-2609.15120", "train-on-test"),
    ("eccv-3d-2607.26889", "test-tuning"),
    ("eccv-video-2608.07663", "train-on-test"),
    ("iclr-video-2604.18367", "test-tuning"),
    ("iclr-efficient-2601.20232", "train-on-test"),
]

ANCHORS = [r"implementation details", r"training details", r"experimental setup",
           r"experimental settings?", r"implementation", r"setup"]


def plant(text, sentence):
    """Insert the sentence after the first full sentence following an anchor heading."""
    for anchor in ANCHORS:
        m = re.search(anchor, text, re.I)
        if not m:
            continue
        end = re.search(r"\.\s", text[m.end():m.end() + 2000])
        if end:
            pos = m.end() + end.end()
            return text[:pos] + sentence + " " + text[pos:], anchor
    raise SystemExit("no anchor found")


def main():
    manifest = {p["id"]: p for p in json.load(open(sys.argv[1]))}
    out = []
    for pid, flaw in CONTROLS:
        src = WORK / pid
        dst = WORK / f"{pid}-flaw"
        dst.mkdir(parents=True, exist_ok=True)
        for name in ("blinded.txt", "paper.txt"):
            text, anchor = plant((src / name).read_text(errors="replace"), FLAWS[flaw])
            (dst / name).write_text(text)
        entry = dict(manifest[pid])
        entry.update({"id": f"{pid}-flaw", "control_of": pid, "planted_flaw": flaw,
                      "planted_sentence": FLAWS[flaw], "anchor": anchor})
        out.append(entry)
        print(f"{pid}: planted '{flaw}' after '{anchor}'", file=sys.stderr)
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
