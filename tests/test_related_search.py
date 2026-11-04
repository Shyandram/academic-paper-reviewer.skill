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
        self.assertEqual(rs.classify(hit(date="2025-06-01"), FP, "on")[1],
                         "prior (arXiv-only, 6+ months before the cutoff)")
        self.assertIn("concurrent", rs.classify(hit(date="2026-02-10"), FP, "on")[1])

    def test_recent_preprint_is_not_required_unless_peer_reviewed(self):
        recent = hit(date="2025-11-01")                         # 4 months before the cutoff
        self.assertIn("recent preprint", rs.classify(recent, FP, "on")[1])
        accepted = hit(date="2025-11-01", comment="Accepted to ICCV 2025")
        self.assertEqual(rs.classify(accepted, FP, "on")[1], "prior (peer-reviewed)")
        journal = hit(date="2025-11-01", journal_ref="IEEE TPAMI 47 (2025)")
        self.assertEqual(rs.classify(journal, FP, "on")[1], "prior (peer-reviewed)")
        workshop_only = hit(date="2025-11-01", comment="12 pages, 5 figures")
        self.assertIn("recent preprint", rs.classify(workshop_only, FP, "on")[1])


class SimilarityTests(unittest.TestCase):
    PAPER = ("We study lane topology reasoning for autonomous driving. Our hierarchical centerline queries "
             "combine point queries and instance queries with cyclic feedback, and a topology head predicts "
             "lane to lane connectivity from fused geometric and semantic features on OpenLane-V2. ") * 3

    def kept(self, title, abstract, label="prior"):
        return {"title": title, "abstract": abstract, "label": label, "url": "u", "date": "2024-01-01"}

    def test_verbatim_copy_is_flagged_as_text_overlap(self):
        copied = ("Our hierarchical centerline queries combine point queries and instance queries with cyclic "
                  "feedback, and a topology head predicts lane to lane connectivity.")
        rows = rs.similarity_report(self.PAPER, [self.kept("Copied source", copied),
                                                 self.kept("Unrelated", "Image super-resolution with diffusion priors and perceptual losses.")])
        src = next(r for r in rows if r["title"] == "Copied source")
        self.assertGreaterEqual(src["shared_8grams"], rs.TEXT_OVERLAP_GRAMS)
        self.assertTrue(any("text overlap" in f for f in src["flags"]))
        other = next(r for r in rows if r["title"] == "Unrelated")
        self.assertEqual(other["shared_8grams"], 0)
        self.assertFalse(any("text overlap" in f for f in other["flags"]))

    def test_closest_prior_ranking_and_duplicates(self):
        close = "Lane topology reasoning with centerline queries and connectivity prediction for driving."
        far = "Medical image segmentation with transformers on MRI volumes."
        rows = rs.similarity_report(self.PAPER, [self.kept("Close", close), self.kept("Close", close),
                                                 self.kept("Far", far), self.kept("Newer close", close, "newer")])
        self.assertEqual(len(rows), 3)                       # duplicate removed
        self.assertEqual(rows[0]["title"], "Close")
        closest = [r["title"] for r in rows if any("closest prior" in f for f in r["flags"])]
        self.assertNotIn("Newer close", closest)             # only prior work counts for novelty


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


class ScoutAndCoverageTests(unittest.TestCase):
    def test_benchmarks_are_found_case_sensitively_with_metrics(self):
        text = ("Table 2: results on COCO and LVIS.\nMethod AP AP50\nOurs 52.1 70.3\n"
                "We also report ImageNet-1K top-1 and ImageNet FID.\nThis is a test.")
        rows = {r["benchmark"]: r for r in rs.find_benchmarks(text)}
        self.assertIn("COCO", rows)
        self.assertIn("AP", rows["COCO"]["metrics"])
        self.assertIn("ImageNet-1K", rows)
        self.assertEqual(rows["ImageNet"]["mentions"], 1)       # the -1K span is not counted twice
        self.assertNotIn("IS", sum((r["metrics"] for r in rows.values()), []))   # "is" is not IS

    def test_scout_returns_prior_rows_first_with_numbers(self):
        kept = [
            {"title": "Recent thing", "label": "recent preprint (arXiv-only, ...)", "date": "2026-01-01",
             "abstract": "We reach 55.0 AP on COCO."},
            {"title": "Strong detector", "label": "prior (peer-reviewed)", "date": "2024-05-01",
             "abstract": "Our detector achieves 58.4 AP on COCO test-dev. It is fast."},
            {"title": "Unrelated", "label": "prior (peer-reviewed)", "date": "2024-05-01",
             "abstract": "Segmentation on ADE20K."},
        ]
        rows = rs.scout_rows(kept, "COCO", "AP")
        self.assertEqual([r["title"] for r in rows], ["Strong detector", "Recent thing"])
        self.assertTrue(rows[0]["can_be_required"] and rows[0]["metric_mentioned"])
        self.assertFalse(rows[1]["can_be_required"])
        self.assertIn("58.4", rows[0]["numbers"])

    def test_query_budget_and_purpose_logging(self):
        with tempfile.TemporaryDirectory() as d:
            fp_path = Path(d) / "fp.json"
            fp_path.write_text(json.dumps(FP))
            ledger = Path(d) / "search_ledger.jsonl"
            for i in range(rs.MAX_QUERIES):
                rs.ledger_write(ledger, {"event": "query", "query": f"q{i}", "purpose": "claim", "tag": "C1"})
            args = type("A", (), {"fp": str(fp_path), "ledger": str(ledger), "query": "lane graph",
                                  "max": 5, "mode": "strict", "purpose": "baseline", "tag": None})
            with self.assertRaises(SystemExit) as cm:
                rs.cmd_search(args)
            self.assertIn("budget", str(cm.exception))
            self.assertEqual(rs.read_ledger(ledger)[-1]["event"], "query_over_budget")

    def test_long_query_is_refused_without_using_budget(self):
        with tempfile.TemporaryDirectory() as d:
            fp_path = Path(d) / "fp.json"
            fp_path.write_text(json.dumps(FP))
            ledger = Path(d) / "search_ledger.jsonl"
            args = type("A", (), {"fp": str(fp_path), "ledger": str(ledger),
                                  "query": "voxel optimization mirror reflection illusion sculpture",
                                  "max": 5, "mode": "strict", "purpose": "claim", "tag": "C1"})
            with self.assertRaises(SystemExit) as cm:
                rs.cmd_search(args)
            self.assertIn("not counted", str(cm.exception))
            events = rs.read_ledger(ledger)
            self.assertEqual([e["event"] for e in events], ["query_too_long"])

    def test_coverage_reports_gaps(self):
        events = [{"event": "query", "purpose": "claim", "tag": "C1"}]
        kept = [{"title": "Old", "label": "prior (peer-reviewed)", "date": "2023-02-01"},
                {"title": "Old", "label": "prior (peer-reviewed)", "date": "2023-02-01"}]
        cov = rs.coverage_report(events, kept, FP, claims=["C1", "C2"])
        self.assertEqual(cov["unique_kept"], 1)
        self.assertEqual(cov["kept_by_label"], {"prior (peer-reviewed)": 1})
        gaps = " ".join(cov["gaps"])
        self.assertIn("no baseline query", gaps)
        self.assertIn("claim C2 has no query", gaps)
        self.assertIn("2025", gaps)

    def test_coverage_flags_claim_whose_queries_kept_nothing(self):
        events = [{"event": "query", "purpose": "claim", "tag": "C1"},
                  {"event": "query_result", "tag": "C1", "returned": 0, "kept": 0},
                  {"event": "query", "purpose": "claim", "tag": "C2"},
                  {"event": "query_result", "tag": "C2", "returned": 9, "kept": 4}]
        gaps = " ".join(rs.coverage_report(events, [], FP, claims=["C1", "C2"])["gaps"])
        self.assertIn("claim C1: its queries kept no results", gaps)
        self.assertNotIn("claim C2:", gaps)

