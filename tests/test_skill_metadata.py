"""The SKILL.md heading version must match its frontmatter version and the changelog."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class VersionTests(unittest.TestCase):
    def test_heading_matches_metadata_and_changelog(self):
        text = (ROOT / "academic-paper-reviewer" / "SKILL.md").read_text()
        meta = re.search(r'^\s*version:\s*"?([\d.]+)"?', text, re.M).group(1)
        heading = re.search(r"^# Academic Paper Reviewer v([\d.]+)", text, re.M).group(1)
        # the first numbered entry that is not withdrawn ("## Unreleased" has no number)
        latest = re.search(r"^## ([\d.]+)(?![\d.])(?! \(withdrawn)", (ROOT / "CHANGELOG.md").read_text(), re.M).group(1)
        self.assertEqual(heading, meta)
        self.assertEqual(latest, meta)


if __name__ == "__main__":
    unittest.main()
