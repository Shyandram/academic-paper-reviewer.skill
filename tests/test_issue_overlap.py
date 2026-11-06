import contextlib
import io as _io
import json
import random
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals"))
import issue_overlap as io  # noqa: E402


REPORT = """## Reviewer: X, Methodology
### Summary
Fine.
### Weaknesses
### W1: No variance
Single runs only.
### W2: Baseline mismatch
Table 2.
### Questions for Authors
Why?
"""

DA = """## Reviewer: Y, Devil's Advocate
## Issue List
### CRITICAL Issues
No CRITICAL issues found.
### MAJOR Issues
| DA-M1 | P1 | Table 2 | confounded | rerun |
## Numerical Sanity Check
ok
"""


class Extraction(unittest.TestCase):
    def test_weaknesses_keep_subitems_and_stop_at_next_section(self):
        w = io.weaknesses(REPORT, "R1")
        self.assertIn("Single runs only", w)
        self.assertIn("Table 2", w)
        self.assertNotIn("Why?", w)
        d = io.weaknesses(DA, "DA")
        self.assertIn("confounded", d)
        self.assertNotIn("Numerical", d)

    def test_blind_hides_sources_and_keeps_key(self):
        data, key = io.blind("p", {"rev_a": "h1", "rev_b": "h2"},
                             {r: r.lower() for r in io.ROLES}, random.Random(1))
        text = json.dumps(data)
        self.assertNotIn("rev_a", text)
        self.assertNotIn("R1", text.replace("panel_", ""))
        self.assertEqual(sorted(v[0] for v in key.values()), ["A"] * 5 + ["H"] * 2)
        self.assertEqual(sorted(v[1] for v in key.values() if v[0] == "A"), sorted(io.ROLES))


class Analysis(unittest.TestCase):
    """Two humans, five AI reviewers (here only R1, R2 and DA raise issues)."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        d = self.tmp / "paper1"
        d.mkdir()
        key = {"P1": ["H", "h1"], "P2": ["H", "h2"]}
        key.update({f"Q{i + 1}": ["A", r] for i, r in enumerate(io.ROLES)})
        (d / "blind_key.json").write_text(json.dumps(key))
        pts = [("P1.1", "P1", False), ("P2.1", "P2", False), ("P2.2", "P2", False),
               ("P2.3", "P2", True),
               ("Q1.1", "Q1", False), ("Q5.1", "Q5", False), ("Q2.1", "Q2", False)]
        ann = {"points": [{"id": i, "reviewer": r, "text": "", "minor": m} for i, r, m in pts],
               "issues": {"P": [{"id": "PI1", "points": ["P1.1", "P2.1"]},   # human consensus
                                {"id": "PI2", "points": ["P2.2"]},
                                {"id": "PI3", "points": ["P2.3"]}],          # minor only
                          "Q": [{"id": "QI1", "points": ["Q1.1", "Q5.1"]},   # R1 + DA
                                {"id": "QI2", "points": ["Q2.1"]}]},
               "cross": [{"p_issue": "PI1", "match": ["QI1"]}, {"p_issue": "PI2", "match": []},
                         {"p_issue": "PI3", "match": []}]}
        (d / "issues.json").write_text(json.dumps(ann))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_metrics(self):
        s, rows = io.analyze(self.tmp, reps=50)
        m = {k: v["mean"] for k, v in s["metrics"].items()}
        self.assertEqual(m["human_issues"], 2)        # the minor-only issue is left out
        self.assertEqual(m["hit"], 0.5)
        self.assertEqual(m["hit_consensus"], 1.0)
        self.assertEqual(m["hit_single"], 0.0)
        self.assertEqual(m["hit_without_da"], 0.5)    # R1 also raised it
        self.assertEqual(m["ai_also_human"], 0.5)
        self.assertEqual(m["human_solo"], 0.5)
        self.assertEqual(s["roles"]["DA"]["own_only"], 0.0)
        self.assertEqual(s["roles"]["R2"]["own_only"], 1.0)
        self.assertEqual(s["roles"]["DA"]["unique_hit"], 0.0)
        self.assertEqual(s["coverage_curve"][-1], 0.5)
        all_issues, _ = io.analyze(self.tmp, reps=50, major_only=False)
        self.assertEqual(all_issues["metrics"]["human_issues"]["mean"], 3)

    def test_markdown_and_json_hold_no_text(self):
        s, rows = io.analyze(self.tmp, reps=50)
        self.assertIn("Hit rate", io.markdown(s))
        out = self.tmp / "n.json"
        with contextlib.redirect_stdout(_io.StringIO()):
            io.main(["analyze", str(self.tmp), "--json", str(out), "--reps", "50"])
        data = json.loads(out.read_text())
        self.assertEqual(data["papers"][0]["paper_id"], "paper1")
        self.assertNotIn("weaknesses", out.read_text())


if __name__ == "__main__":
    unittest.main()
