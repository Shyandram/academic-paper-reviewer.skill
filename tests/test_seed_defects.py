import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals"))
import seed_defects as sd  # noqa: E402

TEXT = "Title\n\nWe train for 100 epochs.\nTable 2: ours 81.2 vs 79.5 baseline\nSame line\nSame line\n"


def anchor(line, occ=0):
    return {"sha256": sd.line_sha(line), "occurrence": occ}


class Apply(unittest.TestCase):
    def test_replace_number_and_insert(self):
        seeds = [
            {"id": "S1", "type": "number", "op": "replace_number",
             "anchor": anchor("Table 2: ours 81.2 vs 79.5 baseline"), "number_index": 1, "old": "81.2", "new": "78.2"},
            {"id": "S2", "type": "leak", "op": "insert_after",
             "anchor": anchor("We train for 100 epochs."), "text": "We tuned on the test set."},
        ]
        out = sd.apply_seeds(TEXT, seeds)
        self.assertIn("Table 2: ours 78.2 vs 79.5 baseline", out)
        self.assertIn("We train for 100 epochs.\nWe tuned on the test set.\nTable 2", out)

    def test_number_index_counts_only_standalone_numbers(self):
        # "Table 2" -> 2 is index 0, then 81.2, 79.5
        line = "Table 2: ours 81.2 vs 79.5 baseline"
        self.assertEqual([m.group() for m in sd.NUM.finditer(line)], ["2", "81.2", "79.5"])

    def test_old_value_must_match(self):
        seeds = [{"id": "S1", "type": "n", "op": "replace_number",
                  "anchor": anchor("Table 2: ours 81.2 vs 79.5 baseline"), "number_index": 1, "old": "79.5",
                  "new": "70"}]
        with self.assertRaises(ValueError):
            sd.apply_seeds(TEXT, seeds)

    def test_occurrence_and_missing_anchor(self):
        seeds = [{"id": "S1", "type": "x", "op": "insert_after", "anchor": anchor("Same line", 1), "text": "X"}]
        self.assertTrue(sd.apply_seeds(TEXT, seeds).endswith("Same line\nSame line\nX\n"))
        seeds[0]["anchor"] = anchor("Same line", 2)
        with self.assertRaises(ValueError):
            sd.apply_seeds(TEXT, seeds)

    def test_two_seeds_on_one_line_refused(self):
        a = anchor("We train for 100 epochs.")
        seeds = [{"id": "S1", "type": "x", "op": "insert_after", "anchor": a, "text": "X"},
                 {"id": "S2", "type": "x", "op": "insert_after", "anchor": a, "text": "Y"}]
        with self.assertRaises(ValueError):
            sd.apply_seeds(TEXT, seeds)


class Cli(unittest.TestCase):
    def test_apply_writes_and_skips_absent_papers(self):
        tmp = tempfile.mkdtemp()
        d = os.path.join(tmp, "iclr26-AAA")
        os.makedirs(d)
        Path(d, "blinded.txt").write_text(TEXT)
        spec = os.path.join(tmp, "spec.json")
        Path(spec).write_text(json.dumps({"papers": {
            "AAA": {"seeds": [{"id": "S1", "type": "x", "op": "insert_after",
                               "anchor": anchor("We train for 100 epochs."), "text": "Planted."}]},
            "BBB": {"seeds": [{"id": "S2", "type": "x", "op": "insert_after",
                               "anchor": anchor("nothing"), "text": "Z"}]}}}))
        self.assertEqual(sd.main(["apply", spec, tmp]), 0)
        self.assertIn("Planted.", Path(d, "blinded.txt").read_text())
        self.assertEqual(sd.main(["check", spec, tmp]), 1)  # check requires every paper


if __name__ == "__main__":
    unittest.main()
