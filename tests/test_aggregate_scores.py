"""Tests for academic-paper-reviewer/scripts/aggregate_scores.py.

Run: python3 -m unittest discover -s tests
"""

import copy
import importlib.util
import json
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "academic-paper-reviewer"
spec = importlib.util.spec_from_file_location("agg", SKILL / "scripts" / "aggregate_scores.py")
agg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agg)

EXAMPLE = json.loads((SKILL / "scripts" / "example_scores.json").read_text())


def uniform(score, confidence=5, overall=None):
    r = {"role": "R", "confidence": confidence,
         "scores": {k: score for k, _ in agg.DIMENSIONS}}
    if overall is not None:
        r["overall"] = overall
    return r


class AggregateTests(unittest.TestCase):
    def test_example_matches_documented_output(self):
        res = agg.aggregate(copy.deepcopy(EXAMPLE))
        self.assertEqual(res["before_composite"], 62.9)
        self.assertEqual(res["panel_composite"], 62.5)
        self.assertEqual(res["suggested_overall"], 4)
        self.assertEqual(res["final_overall_ceiling"], 6)   # DA-C1 downgraded by the EIC
        tr = next(d for d in res["dimensions"] if d["key"] == "technical_rigor")
        self.assertEqual((tr["before_avg"], tr["weighted_avg"]), (61.6, 61.0))

    def test_weights_sum_to_one(self):
        for name, w in agg.PAPER_TYPE_WEIGHTS.items():
            self.assertAlmostEqual(sum(w), 1.0, msg=name)

    def test_confidence_weighting(self):
        data = {"reviewers": [uniform(80, confidence=5), uniform(40, confidence=1)]}
        res = agg.aggregate(data)
        expected = round((80 * 1.0 + 40 * 0.4) / 1.4, 1)
        self.assertEqual(res["dimensions"][0]["weighted_avg"], expected)

    def test_decision_bands(self):
        for score, band in [(90, 6), (85, 6), (84.9, 5), (70, 5), (65, 4),
                            (55, 3), (40, 2), (10, 1)]:
            self.assertEqual(agg.composite_to_overall(score), band, score)

    def test_da_cap_resolvable_vs_not(self):
        base = {"reviewers": [uniform(90)]}
        resolvable = dict(base, da_critical=[{"id": "DA-C1", "resolvable_without_new_data": True}])
        hard = dict(base, da_critical=[{"id": "DA-C1", "resolvable_without_new_data": False}])
        downgraded = dict(base, da_critical=[{"id": "DA-C1", "upheld": False}])
        self.assertEqual(agg.aggregate(resolvable)["final_overall_ceiling"], 4)
        self.assertEqual(agg.aggregate(hard)["final_overall_ceiling"], 3)
        self.assertEqual(agg.aggregate(downgraded)["final_overall_ceiling"], 6)

    def test_ceiling_is_the_cap_not_the_band(self):
        # The composite band is a guideline; only the DA cap is a hard ceiling.
        data = {"reviewers": [uniform(40)], "da_critical": [{"id": "DA-C1"}]}
        res = agg.aggregate(data)
        self.assertEqual(res["suggested_overall"], 2)
        self.assertEqual(res["final_overall_ceiling"], 3)
        self.assertEqual(agg.aggregate({"reviewers": [uniform(40)]})["final_overall_ceiling"], 6)

    def test_eic_weights_change_after_not_before(self):
        strong, weak = uniform(80), uniform(40)
        strong["eic_weight"], weak["eic_weight"] = 1.5, 0.5
        res = agg.aggregate({"reviewers": [strong, weak]})
        self.assertEqual(res["before_composite"], 60.0)
        self.assertEqual(res["panel_composite"], 70.0)   # (80*1.5 + 40*0.5) / 2
        self.assertTrue(res["eic_weighted"])
        self.assertFalse(agg.aggregate({"reviewers": [uniform(70)]})["eic_weighted"])

    def test_eic_weight_out_of_range_exits(self):
        r = uniform(70)
        r["eic_weight"] = 3
        with self.assertRaises(SystemExit):
            agg.aggregate({"reviewers": [r]})

    def test_high_spread_flag(self):
        data = {"reviewers": [uniform(50), uniform(75)]}
        self.assertTrue(agg.aggregate(data)["dimensions"][0]["high_spread"])

    def test_consistency_warning(self):
        data = {"reviewers": [uniform(90, overall=2)]}
        self.assertEqual(len(agg.aggregate(data)["warnings"]), 1)

    def test_paper_type_alias(self):
        data = {"paper_type": "survey", "reviewers": [uniform(70)]}
        self.assertEqual(agg.aggregate(data)["paper_type"], "benchmark")

    def test_venue_profiles_are_complete(self):
        venues = agg.load_venues()
        expected = {"cvpr", "iccv", "eccv", "neurips", "iclr", "icml", "aaai",
                    "acmmm", "tmlr", "tpami", "tip"}
        self.assertEqual(set(venues), expected)
        for key, v in venues.items():
            self.assertEqual(len(v["emphasis"]), len(agg.DIMENSIONS), key)
            self.assertIn(v["scale"]["status"],
                          {"official", "confirmed", "secondary", "assumed", "unpublished"}, key)
            if v["scale"]["type"] != "tmlr":
                self.assertEqual(set(v["scale"]["map"]), {str(i) for i in range(1, 7)}, key)

    def test_example_venue_views(self):
        res = agg.aggregate(copy.deepcopy(EXAMPLE))
        venues = agg.load_venues()
        views = {k: agg.venue_view(res, k, venues[k]) for k in venues}
        self.assertEqual(views["cvpr"]["label"], "4 Borderline Accept")
        self.assertEqual(views["icml"]["label"], "3 Weak accept (leaning accept)")
        self.assertEqual(views["tpami"]["label"], "Major Revision")      # +3 bar
        self.assertEqual(views["iclr"]["subscores"],
                         {"Soundness": 2, "Presentation": 3, "Contribution": 2})
        self.assertEqual(views["tmlr"]["label"], "Accept with minor revision")
        self.assertEqual(views["aaai"]["label"], "6 (Borderline accept)")

    def test_venue_views_respect_da_cap(self):
        data = copy.deepcopy(EXAMPLE)
        data["da_critical"] = [{"id": "DA-C1", "upheld": True, "resolvable_without_new_data": False}]
        res = agg.aggregate(data)
        venues = agg.load_venues()
        for k, v in venues.items():
            self.assertLessEqual(agg.venue_view(res, k, v)["final"], 3, k)
        self.assertEqual(agg.venue_view(res, "tmlr", venues["tmlr"])["subscores"]["Claims & evidence"], "No")

    def test_bar_offset_and_tmlr_without_cap(self):
        res = agg.aggregate({"reviewers": [uniform(72)]})
        venues = agg.load_venues()
        self.assertEqual(agg.venue_view(res, "tpami", venues["tpami"])["band"], 4)  # 72 < 70+3
        self.assertEqual(agg.venue_view(res, "neurips", venues["neurips"])["band"], 5)
        tmlr = agg.venue_view(res, "tmlr", venues["tmlr"])
        self.assertEqual(tmlr["label"], "Accept")

    def test_invalid_input_exits(self):
        with self.assertRaises(SystemExit):
            agg.aggregate({"reviewers": [uniform(70, confidence=9)]})
        with self.assertRaises(SystemExit):
            agg.aggregate({"paper_type": "poem", "reviewers": [uniform(70)]})


if __name__ == "__main__":
    unittest.main()
