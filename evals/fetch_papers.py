#!/usr/bin/env python3
"""Download manifest papers from arXiv and extract blinded text.

For each paper, writes to evals/work/papers/<id>/:
  paper.pdf        the arXiv PDF (untrusted data)
  paper.txt        pdftotext output
  blinded.txt      the text reviewers see: venue/acceptance marks redacted

    python3 evals/fetch_papers.py evals/manifest.json
"""

import json
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

WORK = Path(__file__).resolve().parent / "work" / "papers"

# Lines or phrases that reveal the venue decision. Redacted, not deleted, so
# reviewers know something was removed.
REVEALING = [
    r"published as a conference paper at [^\n]*",
    r"under review as a conference paper at [^\n]*",
    r"this (cvpr|iccv|eccv|wacv)[^\n]*open access version[^\n]*",
    r"except for this watermark[^\n]*",
    r"the final published version[^\n]*",
    r"(accepted|published|to appear)\s+(at|in|to|by)\s+(the\s+)?[^\n]{0,40}(cvpr|eccv|iclr|iccv)[^\n]*",
    r"\b(cvpr|eccv|iclr)\s*(2026|'26)\b[^\n]{0,30}(highlight|oral|poster|accept)[^\n]*",
    r"\b(cvpr|eccv|iclr|iccv)[\s_-]?(2026|26)\b",
    r"(proceedings of the )?(ieee/cvf )?(conference on computer vision and pattern recognition|"
    r"european conference on computer vision|international conference on learning representations)"
    r"\s*\(?(cvpr|eccv|iclr)?\)?\s*,?\s*2026",
]


def blind(text):
    n = 0
    for pat in REVEALING:
        text, k = re.subn(pat, "[REDACTED: venue/acceptance mark]", text, flags=re.I)
        n += k
    return text, n


def main():
    manifest = json.load(open(sys.argv[1]))
    for p in manifest:
        d = WORK / p["id"]
        d.mkdir(parents=True, exist_ok=True)
        pdf = d / "paper.pdf"
        if not pdf.exists() or pdf.stat().st_size < 10_000:
            url = f"https://arxiv.org/pdf/{p['arxiv_id']}"
            req = urllib.request.Request(url, headers={"User-Agent": "paper-review-eval/1.0"})
            for attempt in range(4):
                try:
                    with urllib.request.urlopen(req, timeout=120) as r:
                        pdf.write_bytes(r.read())
                    break
                except Exception as e:
                    print(f"  retry {p['id']}: {e}", file=sys.stderr)
                    time.sleep(5 * 2 ** attempt)
            time.sleep(3)
        if not pdf.read_bytes()[:5] == b"%PDF-":
            print(f"FAILED {p['id']}: not a PDF", file=sys.stderr)
            continue
        txt = d / "paper.txt"
        subprocess.run(["pdftotext", "-layout", str(pdf), str(txt)], check=True)
        blinded, n = blind(txt.read_text(errors="replace"))
        (d / "blinded.txt").write_text(blinded)
        pages = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        npages = re.search(r"Pages:\s+(\d+)", pages)
        print(f"{p['id']}: {npages.group(1) if npages else '?'} pages, "
              f"{len(blinded.split())} words, {n} redactions")


if __name__ == "__main__":
    main()
