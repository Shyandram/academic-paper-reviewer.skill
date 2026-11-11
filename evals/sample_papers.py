#!/usr/bin/env python3
"""Sample recently accepted main-conference papers from arXiv, stratified by topic.

Acceptance comes from the authors' arXiv comment ("Accepted to CVPR 2026",
"Published at ECCV 2026", ...). Workshop, challenge, tutorial and
"submitted/under review" papers are excluded.

Each paper is assigned to exactly one topic (the first matching rule, applied
to title + abstract), and each venue gets one paper per topic, so every venue
covers the same set of distinct topics. These topics mirror the task families
in academic-paper-reviewer/references/cv_review_checklist.md.

    python3 evals/sample_papers.py --seed 7 > evals/manifest.json
"""

import argparse
import json
import random
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

API = "https://export.arxiv.org/api/query"
NS = {"a": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

VENUES = {
    "cvpr": "CVPR 2026",
    "eccv": "ECCV 2026",
    "iclr": "ICLR 2026",
}

# Ordered: the first match wins, so more specific topics come first.
TOPICS = [
    ("medical", r"medical|clinical|patient|radiolog|patholog|\bmri\b|\bct\b|x-ray|endoscop|retina|surgical"),
    ("generation", r"diffusion|text-to-image|text-to-video|image generation|video generation|generative model|\bgan\b|flow matching|image editing|synthesi[sz]"),
    ("vlm", r"vision[- ]language|multimodal (large )?language|\bmllm|\bvlm|large language model|visual question|\bclip\b|captioning|grounding"),
    ("3d", r"\b3d\b|nerf|gaussian splatting|point cloud|novel view|reconstruction|mesh|\bslam\b|multi-view|depth estimation|stereo|pose estimation"),
    ("video", r"\bvideo|tracking|temporal|action recognition|optical flow"),
    ("lowlevel", r"super-resolution|denois|deblur|restoration|derain|dehaz|low-light|image enhancement|compression|inpainting"),
    ("detseg", r"detection|segmentation|instance|panoptic|semantic seg|object detect|open-vocabulary"),
    ("efficient", r"efficien|pruning|quantiz|distillation|lightweight|latency|token (merging|reduction)|sparse"),
    ("representation", r"self-supervised|contrastive|representation learning|pre-?training|foundation model|masked image"),
    ("robustness", r"robust|adversarial|out-of-distribution|domain (adaptation|generalization)|continual|uncertainty|fairness|bias"),
]
EXCLUDE = re.compile(r"workshop|challenge|tutorial|competition|\btrack\b|submitted|@ ?(cvpr|eccv|iclr)|ml4\w+|"
                     r"under review|in submission|rejected|findings|\bdemo\b|"
                     r"tiny paper|blog ?post|extended abstract", re.I)


def accepted_pattern(label):
    return re.compile(r"(accept(ed)?|publish(ed)?|appear(s|ing)?|to appear|"
                      r"camera[- ]ready|main conference|highlight|oral|poster)"
                      r"[^.;]{0,40}" + re.escape(label) + r"|" + re.escape(label)
                      + r"[^.;]{0,15}(\(?(oral|highlight|poster|main)|accept)",
                      re.I)


def query(label, start, size):
    q = f'co:"{label}" AND cat:cs.CV'
    url = API + "?" + urllib.parse.urlencode({
        "search_query": q, "start": start, "max_results": size,
        "sortBy": "submittedDate", "sortOrder": "descending"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(url, timeout=90) as r:
                return ET.fromstring(r.read())
        except Exception as e:  # network hiccups / rate limiting
            print(f"  retry {attempt + 1}: {e}", file=sys.stderr)
            time.sleep(5 * 2 ** attempt)
    sys.exit("arXiv API unreachable")


def topic_of(text):
    for name, pattern in TOPICS:
        if re.search(pattern, text, re.I):
            return name
    return None


def candidates(label, pool):
    pat = accepted_pattern(label)
    out = {}
    for start in range(0, pool, 100):
        root = query(label, start, 100)
        entries = root.findall("a:entry", NS)
        for e in entries:
            comment = " ".join((e.findtext("arxiv:comment", "", NS) or "").split())
            if EXCLUDE.search(comment) or not pat.search(comment):
                continue
            title = " ".join(e.findtext("a:title", "", NS).split())
            abstract = " ".join(e.findtext("a:summary", "", NS).split())
            topic = topic_of(title + " " + abstract)
            if topic is None:
                continue
            arxiv_id = e.findtext("a:id", "", NS).rsplit("/abs/", 1)[-1]
            base = re.sub(r"v\d+$", "", arxiv_id)
            primary = e.find("arxiv:primary_category", NS)
            out.setdefault(base, {
                "arxiv_id": base,
                "title": title,
                "abstract": abstract,
                "topic": topic,
                "comment": comment,
                "primary_category": primary.get("term") if primary is not None else "",
                "published": e.findtext("a:published", "", NS)[:10],
            })
        print(f"  {label}: scanned {start + len(entries)}", file=sys.stderr)
        if len(entries) < 100:
            break
        time.sleep(3)  # arXiv API etiquette
    return list(out.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", type=int, default=500, help="results to scan per venue")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--pool-out", help="also write every eligible candidate here (for curation)")
    args = ap.parse_args()
    pool_dump = {}
    rng = random.Random(args.seed)
    manifest = []
    for key, label in VENUES.items():
        cands = candidates(label, args.pool)
        pool_dump[key] = cands
        by_topic = {}
        for c in cands:
            by_topic.setdefault(c["topic"], []).append(c)
        counts = {t: len(by_topic.get(t, [])) for t, _ in TOPICS}
        print(f"{key}: {len(cands)} eligible; per topic {counts}", file=sys.stderr)
        for topic, _ in TOPICS:
            pool = by_topic.get(topic, [])
            if not pool:
                print(f"  WARNING {key}: no paper for topic '{topic}'", file=sys.stderr)
                continue
            c = rng.choice(pool)
            c.update({"venue": key, "id": f"{key}-{topic}-{c['arxiv_id']}"})
            manifest.append(c)
        time.sleep(3)
    if args.pool_out:
        with open(args.pool_out, "w", encoding="utf-8") as f:
            json.dump(pool_dump, f, indent=1, ensure_ascii=False)
    json.dump(manifest, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
