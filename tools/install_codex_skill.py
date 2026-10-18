#!/usr/bin/env python3
"""Link this checkout into Codex's project or explicit personal skills directory."""

import argparse
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "academic-paper-reviewer"


def install(skills_dir):
    if not (SOURCE / "SKILL.md").is_file():
        raise ValueError("Source SKILL.md is missing")
    skills_dir = Path(skills_dir).expanduser().resolve()
    if skills_dir == SOURCE or SOURCE in skills_dir.parents:
        raise ValueError("The skills directory cannot be inside the skill source")
    target = skills_dir / SOURCE.name
    if target.is_symlink() and target.resolve() == SOURCE:
        return target
    if target.exists() or target.is_symlink():
        raise ValueError(f"Refusing to replace existing path: {target}")
    skills_dir.mkdir(parents=True, exist_ok=True)
    target.symlink_to(os.path.relpath(SOURCE, skills_dir), target_is_directory=True)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", type=Path,
                        default=ROOT / ".agents" / "skills")
    args = parser.parse_args()
    try:
        target = install(args.skills_dir)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"error: {exc}\n")
    print(f"Codex skill linked: {target}")
    print("Start a new session for discovery, or read the linked SKILL.md directly.")


if __name__ == "__main__":
    main()
