import argparse
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "evals" / "split"))
import run_split as rs  # noqa: E402

PID = "iclr26-TEST"


def run(argv):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rs.main(argv)
    return buf.getvalue()


class SplitPipeline(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        shutil.copytree(REPO / "academic-paper-reviewer", self.tmp / "academic-paper-reviewer")
        shutil.copytree(REPO / "evals" / "split", self.tmp / "evals" / "split")
        paper = self.tmp / "evals" / "work" / "papers" / PID
        paper.mkdir(parents=True)
        (paper / "blinded.txt").write_text("UNREDACTED SECRET LINE\nMethod text.")
        self.p = rs.paths(self.tmp, PID)
        self.p["p0"].mkdir(parents=True)
        (self.p["p0"] / "reviewer_copy.txt").write_text("[redacted]\nMethod text.")
        (self.p["p0"] / "card.md").write_text("Panel card")
        (self.p["p0"] / "paper_memory.md").write_text("C1: claim (Sec. 1)")
        (self.p["p0"] / "panel.json").write_text('{"paper_type": "empirical"}')
        (self.p["p0"] / "integrity.json").write_text('{"findings": ["INJECTED TEXT"]}')
        self.base = ["--id", PID, "--root", str(self.tmp), "--cutoff", "2025-09-24"]

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_prompts_have_no_placeholders(self):
        for phase in ("phase0", "check", "eic"):
            out = run(["prompt", phase] + self.base)
            self.assertNotRegex(out, r"\{[A-Z_]+\}", phase)
            self.assertIn("2025-09-24", out)
        for role in rs.ROLES:
            out = run(["prompt", "reviewer", "--role", role] + self.base)
            self.assertNotRegex(out, r"\{[A-Z_]+\}", role)
            self.assertIn(rs.ROLES[role][1], out)

    def test_check_pipeline_prompts(self):
        panel = run(["prompt", "panel", "--pipeline", "check"] + self.base)
        self.assertNotRegex(panel, r"\{[A-Z_]+\}")
        self.assertIn("do not launch subagents", panel)
        self.assertIn("Do not run Phases 1.5, 1.6 or 2 now", panel)
        check = run(["prompt", "check"] + self.base)
        self.assertIn("report_checker_agent.md", check)
        self.assertIn("factually accurate", check)
        self.assertIn("checker_estimate.json", check)
        self.assertLess(check.index("checker_estimate.json"), check.index("**Phase 1.5**"))
        resumed = run(["prompt", "eic", "--resumed"] + self.base)
        fresh = run(["prompt", "eic"] + self.base)
        self.assertNotRegex(resumed, r"\{[A-Z_]+\}")
        self.assertTrue(resumed.startswith("## Phase 2 (resumed context)"))  # no repeated rules
        self.assertIn("Evaluation rules", fresh)
        self.assertIn("eic.json", resumed)
        self.assertIn("checker_weights", resumed)
        novelty = run(["prompt", "novelty"] + self.base)
        self.assertNotRegex(novelty, r"\{[A-Z_]+\}")
        self.assertIn("novelty_update", novelty)
        self.assertIn("Change nothing else", novelty)

    def test_shared_prefix_is_redacted_and_role_free(self):
        a = argparse.Namespace(
            id=PID, root=str(self.tmp), venue="iclr", venue_name="ICLR", lit="strict",
            cutoff="2025-09-24")
        text = rs.shared_text(a)
        self.assertIn("[redacted]", text)
        self.assertIn("C1: claim", text)
        self.assertNotIn("UNREDACTED SECRET LINE", text)
        self.assertNotIn("INJECTED TEXT", text)
        self.assertNotRegex(text, r"\{(ID|ROOT|RES|SKILL|PAPER|COPY|VENUE_NAME|LIT|CUTOFF)\}")
        self.assertNotIn("<role_file", text)  # the role file goes in the user prompt

    def test_deny_rules_hide_other_reports_and_findings(self):
        rules = rs.deny_rules(self.tmp, PID, "R2")
        joined = "\n".join(rules)
        self.assertIn("reports/R1/**", joined)
        self.assertIn("reports/DA/**", joined)
        self.assertNotIn("reports/R2/", joined)
        self.assertIn("integrity.json", joined)
        self.assertIn(f"papers/{PID}/**", joined)
        self.assertTrue(all(r.startswith("Read(./") for r in rules))

    def test_gap_scout_sees_the_copy_only(self):
        joined = "\n".join(rs.deny_rules(self.tmp, PID, "GAP"))
        for k in rs.ROLES:
            self.assertIn(f"reports/{k}/**", joined)
        self.assertIn("check/**", joined)
        self.assertIn("integrity.json", joined)
        self.assertNotIn("phase0/**", joined)          # the redacted copy stays readable
        self.assertIn("gaps/**", "\n".join(rs.deny_rules(self.tmp, PID, "R1")))
        text = run(["prompt", "gaps"] + self.base)
        self.assertIn("gap_scout_agent.md", text)
        self.assertIn("reviewer_copy.txt", text)
        self.assertNotRegex(text, r"\{(RES|SKILL|COPY|VENUE_NAME)\}")

    def write_reviewers(self, missing=()):
        for i, key in enumerate(rs.ROLES):
            if key in missing:
                continue
            d = self.p["reports"] / key
            d.mkdir(parents=True, exist_ok=True)
            s = {"role": "ignored", "confidence": 4, "overall": 3 + (i % 2), "pool_position": 40 + 5 * i,
                 "scores": {k: 50 + i for k in ("technical_rigor", "clarity", "novelty", "significance",
                                                "experimental_validation", "reproducibility", "ethics")},
                 "da_critical": [], "recognized": False}
            if key == "DA":
                s["da_critical"] = [{"id": "DA-C1", "resolvable_without_new_data": True}]
            (d / "scores.json").write_text(json.dumps(s))
            (d / "report.md").write_text(f"report {key}")

    def test_before_and_finish(self):
        self.write_reviewers()
        run(["before"] + self.base)
        before = json.loads((self.p["res"] / "scores_before.json").read_text())
        self.assertEqual([r["role"] for r in before["reviewers"]],
                         [v[0] for v in rs.ROLES.values()])
        self.assertTrue(before["da_critical"][0]["upheld"])
        self.assertTrue((self.p["res"] / "before.json").exists())

        self.p["eic"].mkdir(parents=True)
        (self.p["eic"] / "eic.json").write_text(json.dumps({
            "final_overall": 4, "eic_pool_position": 61,
            "eic_weights": {"R1": 1.5, "R2": 1.0, "R3": 0.5, "R4": 1.0, "DA": 1.0},
            "da_rulings": [{"id": "DA-C1", "upheld": False, "resolvable_without_new_data": True}],
            "top_concerns": ["a"], "recognized": False, "injection_found": None, "notes": ""}))
        (self.p["eic"] / "decision.md").write_text("decision text")
        self.p["runs"].mkdir(parents=True)
        for name, cost in (("phase0", 0.2), ("R1", 0.3), ("eic", 0.5)):
            (self.p["runs"] / f"{name}.json").write_text(json.dumps({
                "total_cost_usd": cost, "num_turns": 3, "duration_ms": 1000,
                "usage": {"cache_read_input_tokens": 100, "output_tokens": 10}}))
        run(["finish"] + self.base)

        scores = json.loads((self.p["res"] / "scores.json").read_text())
        self.assertEqual(scores["reviewers"][0]["eic_weight"], 1.5)
        self.assertFalse(scores["da_critical"][0]["upheld"])
        summary = json.loads((self.p["res"] / "summary.json").read_text())
        self.assertEqual(summary["final_overall"], 4)
        self.assertEqual(summary["eic_pool_position"], 61)
        self.assertEqual(summary["da_critical_raised"], 1)
        self.assertEqual(summary["da_critical_upheld"], 0)
        self.assertIsInstance(summary["official_rating"], (int, float))
        runlog = json.loads((self.p["res"] / "run.json").read_text())
        self.assertAlmostEqual(runlog["total_cost_usd"], 1.0)
        self.assertEqual(runlog["tokens"]["cache_read"], 300)
        self.assertIsNone(runlog["phases"]["R2"])
        review = (self.p["res"] / "review.md").read_text()
        self.assertIn("report DA", review)
        self.assertIn("decision text", review)
        self.assertIn("(missing)", review)  # no check phase output
        self.assertEqual(summary["pipeline"], "split")

    def test_finish_records_check_pipeline(self):
        self.write_reviewers()
        run(["before"] + self.base)
        self.p["eic"].mkdir(parents=True)
        (self.p["eic"] / "eic.json").write_text(json.dumps({
            "final_overall": 3, "eic_pool_position": 40, "eic_weights": {}, "da_rulings": []}))
        self.p["runs"].mkdir(parents=True)
        (self.p["runs"] / "panel.json").write_text(json.dumps({"total_cost_usd": 1.5}))
        self.p["check"].mkdir(parents=True)
        (self.p["check"] / "checker_estimate.json").write_text(json.dumps(
            {"pool_position": 35, "overall": 3, "reasons": "x"}))
        run(["finish", "--pipeline", "check"] + self.base)
        summary = json.loads((self.p["res"] / "summary.json").read_text())
        self.assertEqual(summary["pipeline"], "check")
        runlog = json.loads((self.p["res"] / "run.json").read_text())
        self.assertAlmostEqual(runlog["phases"]["panel"]["cost_usd"], 1.5)
        self.assertIn("panel_rating", summary)
        self.assertIn("decision_with_lean", summary)
        self.assertEqual(summary["checker_pool_position"], 35)   # recorded, never averaged
        self.assertEqual(summary["checker_overall"], 3)
        self.assertEqual(summary["eic_pool_position"], 40)
        self.assertIn("check pipeline", (self.p["res"] / "review.md").read_text())

    def test_before_requires_all_five(self):
        self.write_reviewers(missing=("R3",))
        with self.assertRaises(SystemExit):
            run(["before"] + self.base)


if __name__ == "__main__":
    unittest.main()
