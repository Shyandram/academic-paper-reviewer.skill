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


class GapScout(unittest.TestCase):
    def test_gap_list_is_an_optional_source(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            for r in io.ROLES:
                (tmp / "reports" / r).mkdir(parents=True)
                (tmp / "reports" / r / "report.md").write_text(DA if r == "DA" else REPORT)
            (tmp / "gaps").mkdir()
            (tmp / "gaps" / "gaps.md").write_text(
                "## Anticipated Reviewer Concerns\n- G1 [baselines] no comparison with X (Table 2)\n")
            self.assertEqual(sorted(io.ai_reports(tmp)), sorted(io.ROLES))
            reps = io.ai_reports(tmp, gaps=True)
            self.assertIn(io.GAP, reps)
            self.assertIn("comparison with X", io.weaknesses(reps[io.GAP], io.GAP))
        finally:
            shutil.rmtree(tmp)


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

    def test_misses_status_and_categories(self):
        ann = json.loads((self.tmp / "paper1" / "issues.json").read_text())
        ann["cross"][1]["related"] = ["QI2"]
        (self.tmp / "paper1" / "issues.json").write_text(json.dumps(ann))
        rows, ai = io.human_issue_status(self.tmp / "paper1")
        self.assertEqual({r["issue_id"]: r["status"] for r in rows},
                         {"PI1": "hit", "PI2": "related"})   # PI3 is minor only
        self.assertEqual(len(ai), 2)
        out = self.tmp / "m"
        with contextlib.redirect_stdout(_io.StringIO()):
            io.main(["misses", str(self.tmp), "--out", str(out)])
            (out / "l.jsonl").write_text(
                json.dumps({"paper_id": "paper1", "issue_id": "PI1", "topic": "baselines"}) + "\n"
                + json.dumps({"paper_id": "paper1", "issue_id": "PI2", "topic": "theory"}) + "\n")
            io.main(["categories", "--issues", str(out / "human_issues.jsonl"), "--labels",
                     str(out / "l.jsonl"), "--fields", "topic", "--json", str(out / "c.json"),
                     "--reps", "20"])
        c = json.loads((out / "c.json").read_text())
        self.assertEqual(c["topic"]["baselines"]["hit"], 1.0)
        self.assertEqual(c["topic"]["theory"]["status"]["related"], 1)
        self.assertEqual(c["consensus"]["2+"]["hit"], 1.0)
        self.assertNotIn("points", (out / "c.json").read_text())

    def test_extra_list_match_round_trip(self):
        m, ex, mo = self.tmp / "m", self.tmp / "ex", self.tmp / "mo"
        (ex / "paper1").mkdir(parents=True)
        (ex / "paper1" / "gaps.md").write_text("- G1 a\n- G2 b\n")
        with contextlib.redirect_stdout(_io.StringIO()), \
                contextlib.redirect_stderr(_io.StringIO()):
            io.main(["misses", str(self.tmp), "--out", str(m)])
            io.main(["match-prepare", str(self.tmp), "--issues", str(m / "human_issues.jsonl"),
                     "--extra", str(ex), "--out", str(mo)])
            key = json.loads((mo / "paper1" / "match_key.json").read_text())
            self.assertEqual(sorted(v[0] for v in key["items"].values()),
                             ["extra", "extra", "panel", "panel"])
            first = next(k for k, v in key["items"].items() if v == ["extra", "g0"])
            ann = [{"human": "H1", "match": [], "related": []},
                   {"human": "H2", "match": [first], "related": []}]
            (mo / "paper1" / "matched.json").write_text(json.dumps(ann))
            io.main(["match-score", str(mo), "--issues", str(m / "human_issues.jsonl"),
                     "--k", "1", "--json", str(mo / "s.json"), "--reps", "20"])
        s = json.loads((mo / "s.json").read_text())["hit"]
        self.assertEqual(s["extra"]["count"], 1)
        self.assertEqual(s["extra_top1"]["count"], 1)
        self.assertEqual(s["panel"]["count"], 0)

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
