import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals"))
import codex_budget_guard as g  # noqa: E402

PRICES = dict(price_in=1.0, price_cached=0.05, price_out=5.0)


def tc(inp, cached, out):
    return json.dumps({"type": "event_msg", "payload": {"type": "token_count", "info": {
        "total_token_usage": {"input_tokens": inp, "cached_input_tokens": cached, "output_tokens": out}}}})


class Usage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.day = os.path.join(self.tmp, "2026", "11", "10")
        os.makedirs(self.day)

    def write(self, name, lines):
        with open(os.path.join(self.day, name), "w") as f:
            f.write("\n".join(lines) + "\n")

    def test_last_cumulative_count_per_file(self):
        self.write("a.jsonl", ['{"type":"session_meta"}', tc(100, 0, 10), "not json", tc(1000, 800, 50)])
        self.assertEqual(g.session_usage(self.tmp),
                         {"input_tokens": 1000, "cached_input_tokens": 800, "output_tokens": 50})

    def test_files_are_summed(self):
        self.write("a.jsonl", [tc(1000, 800, 50)])
        self.write("b.jsonl", [tc(500, 0, 5)])
        self.assertEqual(g.session_usage(self.tmp)["input_tokens"], 1500)

    def test_cost(self):
        u = {"input_tokens": 3_767_886, "cached_input_tokens": 3_627_807, "output_tokens": 24_327}
        self.assertAlmostEqual(g.cost(u, **PRICES), 0.4436, places=3)

    def test_no_prices_refuses(self):
        self.assertEqual(g.main(["--sessions", self.tmp, "--budget", "1", "--pidfile", "x", "--flag", "y"]), 2)


class Stops(unittest.TestCase):
    """Soft stop, then hard stop, against a real process group."""

    def test_soft_then_hard(self):
        tmp = tempfile.mkdtemp()
        day = os.path.join(tmp, "s")
        os.makedirs(day)
        log, pidf, flag = os.path.join(day, "r.jsonl"), os.path.join(tmp, "pid"), os.path.join(tmp, "flag")
        open(log, "w").write(tc(10_000, 0, 0) + "\n")  # $0.01

        def start():
            p = subprocess.Popen(["sleep", "60"], start_new_session=True)
            open(pidf, "w").write(str(p.pid))
            return p

        p1 = start()
        args = ["--sessions", tmp, "--budget", "1", "--pidfile", pidf, "--flag", flag, "--interval", "0.2",
                "--price-in", "1", "--price-cached", "0.05", "--price-out", "5"]
        t = threading.Thread(target=g.main, args=(args,), daemon=True)
        t.start()
        time.sleep(0.6)
        self.assertIsNone(p1.poll())  # under the soft limit
        open(log, "a").write(tc(750_000, 0, 0) + "\n")  # $0.75 >= 70%
        p1.wait(timeout=10)
        self.assertTrue(open(flag).read().startswith("soft"))
        p2 = start()
        time.sleep(0.6)
        self.assertIsNone(p2.poll())  # soft fires once
        open(log, "a").write(tc(900_000, 0, 30_000) + "\n")  # $1.05
        p2.wait(timeout=10)
        t.join(timeout=10)
        self.assertFalse(t.is_alive())
        self.assertTrue(open(flag).read().startswith("hard"))


if __name__ == "__main__":
    unittest.main()
