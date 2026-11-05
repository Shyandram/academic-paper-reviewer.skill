import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals"))
import iclr_calibration as cal  # noqa: E402


class CalibrationMath(unittest.TestCase):
    def test_spearman_and_ties(self):
        self.assertAlmostEqual(cal.spearman([1, 2, 3, 4], [10, 20, 30, 40]), 1.0)
        self.assertAlmostEqual(cal.spearman([1, 2, 3, 4], [4, 3, 2, 1]), -1.0)
        self.assertEqual(cal.ranks([5, 1, 5]), [2.5, 1.0, 2.5])

    def test_accepted_labels(self):
        self.assertTrue(cal.accepted("Accept (Oral)"))
        self.assertTrue(cal.accepted("Conditional Accept (Poster)"))
        for d in ("Reject", "Withdrawn", "Desk rejected"):
            self.assertFalse(cal.accepted(d))

    def test_auc(self):
        self.assertAlmostEqual(cal.auc([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1]), 1.0)
        self.assertAlmostEqual(cal.auc([1, 1, 1, 1], [0, 1, 0, 1]), 0.5)
        self.assertAlmostEqual(cal.auc([0.1, 0.4, 0.35, 0.8], [0, 0, 1, 1]), 0.75)

    def test_fit_recovers_weights_with_constant_column(self):
        rng = random.Random(1)
        X = [[rng.uniform(0, 100) for _ in range(6)] + [100.0] for _ in range(80)]
        y = [1 + 0.05 * x[0] - 0.02 * x[3] for x in X]
        w = cal.fit_linear(X, y)
        for x, t in zip(X, y):
            self.assertAlmostEqual(cal.predict(w, x), t, places=4)

    def test_draw_excludes_unscored_and_splits(self):
        rows = [{"paper_id": f"p{i}", "scores": [] if i % 10 == 0 else [3, 5, 6],
                 "accepted": i % 3 == 0} for i in range(400)]
        picked, kept = cal.draw(rows, n=300, train=150, seed=7)
        self.assertEqual(len(picked), 300)
        self.assertTrue(all(r["scores"] for r in kept))
        self.assertEqual(sum(r["split"] == "train" for r in kept), 150)
        self.assertTrue(all(r["one_human"] in r["scores"] for r in kept))
        _, again = cal.draw([dict(r) for r in rows], n=300, train=150, seed=7)
        self.assertEqual([r["paper_id"] for r in kept], [r["paper_id"] for r in again])

    def test_title_match(self):
        hits = [{"title": "Something Else Entirely"},
                {"title": "DataEnvGym: Data Generation Agents in Teacher Environments with "
                          "Student Feedback"}]
        t = "DataEnvGym: Data generation agents in teacher environments with student feedback"
        self.assertIs(cal.best_match(t, hits), hits[1])
        self.assertIsNone(cal.best_match("A different paper about graphs", hits))

    def test_evaluate_end_to_end(self):
        rng = random.Random(3)
        rows, feats = [], {}
        for i in range(120):
            q = rng.uniform(1, 9)
            scores = [max(1, min(10, round(q + rng.gauss(0, 1.5)))) for _ in range(3)]
            rows.append({"paper_id": f"p{i}", "split": "train" if i < 60 else "test",
                         "scores": scores, "one_human": scores[0], "other_human": scores[1],
                         "mean_human": sum(scores) / 3, "accepted": q > 6,
                         "decision": "Withdrawn" if q < 2 else "Reject"})
            feats[f"p{i}"] = {d: 10 * q + rng.gauss(0, 5) for d in cal.DIMS}
        res = cal.evaluate(rows, feats, reps=200)
        vals = {m["metric"]: m["value"] for m in res["all_scored"]["results"]}
        self.assertGreater(vals["spearman(AI, one human)"], 0.5)
        self.assertGreater(vals["AUC(AI score -> accept)"], 0.8)
        self.assertEqual(res["n_test"], 60)
        sub = res["without_withdrawn"]
        self.assertLess(sub["n_test"], 60)
        self.assertEqual(sub["n_test"], sum(1 for r in rows if r["split"] == "test"
                                            and r["decision"] != "Withdrawn"))


if __name__ == "__main__":
    unittest.main()
