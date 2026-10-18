# Repository workflow

This repository develops a Markdown skill for Codex and Claude, plus Python
standard-library tools. Read `README.md` before changing installation behavior.
Edit skill sources under `academic-paper-reviewer/`; rebuild the tracked archive
with `python3 tools/build_skill.py` when sources change. Do not hand-edit the ZIP.

Validate changes from the repository root:

```bash
python3 -m unittest discover -s tests -v
python3 tools/build_skill.py --check
```

Use `python3 tools/install_codex_skill.py` for an ignored project-local skill link.
Do not overwrite personal skills. Keep manuscript and review artifacts out of
commits. Cloud tasks already have an isolated checkout; do not create worktrees
unless explicitly requested. Agent role files are review instructions, not
background services. No credentials or external dependencies are required for
development tests or score aggregation.
