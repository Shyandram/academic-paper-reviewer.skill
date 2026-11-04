"""Offline tests for academic-paper-reviewer/scripts/related_search.py (no network).

Run: python3 -m unittest discover -s tests
"""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "academic-paper-reviewer"
spec = importlib.util.spec_from_file_location("rs", SKILL / "scripts" / "related_search.py")
rs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rs)

FP = {
    "title": "TopoHR: Hierarchical Centerline Representation for Cyclic Topology Reasoning in Driving Scenes",
    "method_names": ["TopoHR"],
    "authors": ["Wei Zhang", "Li Chen", "Ming Liu"],
    "arxiv_ids": ["2604.24119"],
    "urls": ["https://github.com/example/topohr"],
    "distinctive_phrases": ["cyclic feedback between point and instance queries"],
    "cutoff_date": "2026-03-01",
}


def hit(**kw):
    base = {"title": "A study of lane graph learning", "abstract": "", "url": "https://arxiv.org/abs/2401.00001",
            "date": "2025-06-01", "authors": ["A. Other"]}
    base.update(kw)
    return base


class QueryGuardTests(unittest.TestCase):
    def test_refuses_method_name_author_id_and_title(self):
        self.assertIsNotNone(rs.check_query("TopoHR lane topology", FP))
        self.assertIsNotNone(rs.check_query("centerline topology Zhang", FP))
        self.assertIsNotNone(rs.check_query("2604.24119", FP))
        self.assertIsNotNone(rs.check_query(
            "hierarchical centerline representation cyclic topology reasoning driving", FP))

    def test_allows_concept_queries(self):
        self.assertIsNone(rs.check_query("lane topology reasoning centerline detection", FP))


class SelfExclusionTests(unittest.TestCase):
    def test_own_arxiv_version_is_dropped(self):
        keep, why = rs.classify(hit(title=FP["title"], url="https://arxiv.org/abs/2604.24119v2"), FP, "on")
        self.assertFalse(keep)
        self.assertIn("title", why)

    def test_method_name_in_abstract_is_dropped(self):
        keep, _ = rs.classify(hit(abstract="We compare against TopoHR and improve OLS."), FP, "on")
        self.assertFalse(keep)

    def test_same_id_and_code_url_are_dropped(self):
        self.assertFalse(rs.classify(hit(url="https://arxiv.org/pdf/2604.24119"), FP, "on")[0])
        self.assertFalse(rs.classify(hit(url="https://github.com/example/topohr/issues/3"), FP, "on")[0])

    def test_distinctive_phrase_is_dropped(self):
        keep, _ = rs.classify(hit(abstract="We add cyclic feedback between point and instance queries."), FP, "on")
        self.assertFalse(keep)

    def test_author_overlap_near_cutoff_dropped_but_old_work_kept(self):
        near = hit(authors=["Wei Zhang", "Li Chen"], date="2026-01-15")
        old = hit(authors=["Wei Zhang", "Li Chen"], date="2022-05-01")
        self.assertFalse(rs.classify(near, FP, "on")[0])
        self.assertTrue(rs.classify(old, FP, "on")[0])


class OutcomeLeakTests(unittest.TestCase):
    def test_openreview_and_acceptance_lists_are_blocked(self):
        for url in ("https://openreview.net/forum?id=abc123",
                    "https://cvpr.thecvf.com/Conferences/2026/AcceptedPapers",
                    "https://example.org/eccv2026/accepted-papers",
                    "https://papercopilot.com/paper-list/cvpr"):
            self.assertFalse(rs.classify(hit(url=url), FP, "on")[0], url)


class DateTests(unittest.TestCase):
    def test_post_cutoff_strict_dropped_on_labelled(self):
        h = hit(date="2026-05-01")
        self.assertFalse(rs.classify(h, FP, "strict")[0])
        keep, label = rs.classify(h, FP, "on")
        self.assertTrue(keep)
        self.assertIn("newer", label)

    def test_prior_and_concurrent_labels(self):
        self.assertEqual(rs.classify(hit(date="2025-06-01"), FP, "on"), (True, "prior"))
        self.assertIn("concurrent", rs.classify(hit(date="2026-02-10"), FP, "on")[1])


class LedgerTests(unittest.TestCase):
    def test_every_decision_is_logged(self):
        with tempfile.TemporaryDirectory() as d:
            ledger = str(Path(d) / "ledger.jsonl")
            kept = rs.filter_hits([hit(), hit(title=FP["title"])], FP, "on", ledger, "test")
            with open(ledger) as f:
                rows = [json.loads(l) for l in f]
        self.assertEqual(len(kept), 1)
        self.assertEqual([r["event"] for r in rows], ["keep", "drop"])


if __name__ == "__main__":
    unittest.main()
