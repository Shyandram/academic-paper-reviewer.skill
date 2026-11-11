#!/usr/bin/env python3
"""Validate the skill source and package it as academic-paper-reviewer.skill.

    python3 tools/build_skill.py            # validate + build
    python3 tools/build_skill.py --check    # validate only

Checks:
  * SKILL.md frontmatter has `name` and `description` (<= 1024 chars)
  * every `agents/…`, `references/…`, `templates/…`, `scripts/…`, `examples/…`
    path mentioned in any Markdown file exists
  * scripts/aggregate_scores.py runs on scripts/example_scores.json
  * no leftover placeholders such as TODO/FIXME, and no e-mail addresses

The archive is deterministic (sorted entries, fixed timestamps, no extra
metadata) so rebuilding unchanged sources yields an identical file.
"""

import argparse
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_NAME = "academic-paper-reviewer"
SRC = ROOT / SKILL_NAME
OUT = ROOT / f"{SKILL_NAME}.skill"
FIXED_TIME = (2026, 1, 1, 0, 0, 0)
EXCLUDE = {"__pycache__", ".DS_Store"}
PATH_RE = re.compile(r"`((?:agents|references|templates|scripts|examples)/[\w./-]+)`")


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return None
    fields = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip().strip('"')
    return fields


def validate():
    errors = []
    skill_md = SRC / "SKILL.md"
    if not skill_md.exists():
        return [f"missing {skill_md}"]
    fm = frontmatter(skill_md.read_text(encoding="utf-8"))
    if fm is None:
        errors.append("SKILL.md: missing YAML frontmatter")
    else:
        if fm.get("name") != SKILL_NAME:
            errors.append(f"SKILL.md: name must be '{SKILL_NAME}'")
        desc = fm.get("description", "")
        if not desc:
            errors.append("SKILL.md: missing description")
        elif len(desc) > 1024:
            errors.append(f"SKILL.md: description is {len(desc)} chars (max 1024)")

    for md in sorted(SRC.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        for ref in PATH_RE.findall(text):
            if not (SRC / ref).exists():
                errors.append(f"{md.relative_to(ROOT)}: references missing file `{ref}`")
        if re.search(r"\b(TODO|FIXME|XXX)\b", text):
            errors.append(f"{md.relative_to(ROOT)}: leftover TODO/FIXME/XXX")
        if re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", text):
            errors.append(f"{md.relative_to(ROOT)}: contains an e-mail address")

    result = subprocess.run(
        [sys.executable, "scripts/aggregate_scores.py", "scripts/example_scores.json"],
        cwd=SRC, capture_output=True, text=True)
    if result.returncode != 0:
        errors.append(f"aggregate_scores.py failed: {result.stderr.strip()}")
    return errors


def build():
    files = sorted(p for p in SRC.rglob("*")
                   if p.is_file() and not EXCLUDE.intersection(p.parts))
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in files:
            arcname = path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(arcname, date_time=FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if path.suffix == ".py" else 0o644) << 16
            zf.writestr(info, path.read_bytes())
    return len(files)


def main():
    ap = argparse.ArgumentParser(description="Validate and package the skill.")
    ap.add_argument("--check", action="store_true", help="validate only, do not build")
    args = ap.parse_args()
    errors = validate()
    if errors:
        print("Validation failed:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print("Validation passed.")
    if not args.check:
        n = build()
        print(f"Built {OUT.relative_to(ROOT)} ({n} files).")


if __name__ == "__main__":
    main()
