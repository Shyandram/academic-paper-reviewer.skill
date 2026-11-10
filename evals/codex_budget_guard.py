#!/usr/bin/env python3
"""Per-paper API budget guard for Codex review jobs.

Codex has no spending cap of its own. This guard runs beside `codex exec`, reads the
cumulative token counts that Codex writes to its session logs, prices them with the
run's price_* keys (USD per 1M tokens) and stops the review when the estimate crosses
the budget:

  soft limit (default 70% of the budget): stop the running turn once and write "soft"
    to the flag file; the workflow then resumes the session with a wrap-up prompt
    (write the deliverables now from what is already done);
  hard limit (the budget): stop again and write "hard"; the workflow does not resume.

The process to stop is the process group whose id is in --pidfile (the workflow starts
each `codex exec` with setsid and writes its pid there). Stdlib only.

    python3 codex_budget_guard.py --sessions ~/.codex/sessions --budget 1.0 \
        --pidfile R/.codex_pid --flag R/budget_stop.txt
"""
import argparse
import glob
import json
import os
import signal
import sys
import time

KEYS = ("input_tokens", "cached_input_tokens", "output_tokens")


def session_usage(sessions):
    """Token totals summed over session files, taking each file's last cumulative count.

    A resumed session may continue an existing file or start a new one; summing the
    per-file totals never undercounts (it can only overcount), which is the safe side
    for a cap.
    """
    total = dict.fromkeys(KEYS, 0)
    for f in sorted(glob.glob(os.path.join(sessions, "**", "*.jsonl"), recursive=True)):
        last = None
        try:
            with open(f, errors="replace") as fh:
                for line in fh:
                    if '"total_token_usage"' not in line:
                        continue
                    try:
                        last = json.loads(line)["payload"]["info"]["total_token_usage"]
                    except (ValueError, KeyError, TypeError):
                        continue
        except OSError:
            continue
        if last:
            for k in KEYS:
                total[k] += int(last.get(k) or 0)
    return total


def cost(usage, price_in, price_cached, price_out):
    fresh = max(usage["input_tokens"] - usage["cached_input_tokens"], 0)
    return (fresh * price_in + usage["cached_input_tokens"] * price_cached
            + usage["output_tokens"] * price_out) / 1e6


def stop(pidfile, grace=20):
    try:
        pid = int(open(pidfile).read().strip())
    except (OSError, ValueError):
        return False
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(pid, sig)
        except ProcessLookupError:
            return True
        except PermissionError:
            return False
        for _ in range(grace):
            time.sleep(1)
            try:
                os.killpg(pid, 0)
            except ProcessLookupError:
                return True
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--sessions", required=True)
    ap.add_argument("--budget", type=float, required=True, help="USD cap per paper")
    ap.add_argument("--soft", type=float, default=0.7, help="fraction of the budget that starts the wrap-up")
    ap.add_argument("--pidfile", required=True)
    ap.add_argument("--flag", required=True)
    ap.add_argument("--interval", type=float, default=10)
    ap.add_argument("--price-in", type=float, default=float(os.environ.get("PRICE_IN") or 0))
    ap.add_argument("--price-cached", type=float, default=float(os.environ.get("PRICE_CACHED") or 0))
    ap.add_argument("--price-out", type=float, default=float(os.environ.get("PRICE_OUT") or 0))
    a = ap.parse_args(argv)
    if a.budget <= 0 or not (a.price_in or a.price_cached or a.price_out):
        print("budget guard: no budget or no prices; the guard cannot cap this run", file=sys.stderr)
        return 2
    stage = None
    while True:
        c = cost(session_usage(a.sessions), a.price_in, a.price_cached, a.price_out)
        target = "hard" if c >= a.budget else "soft" if c >= a.soft * a.budget else None
        if target and target != stage and not (stage == "hard"):
            with open(a.flag, "w") as fh:
                fh.write(f"{target} {c:.4f}\n")
            print(f"budget guard: estimated ${c:.2f} of ${a.budget:.2f}; {target} stop", file=sys.stderr)
            stop(a.pidfile)
            stage = target
            if stage == "hard":
                return 0
        time.sleep(a.interval)


if __name__ == "__main__":
    sys.exit(main())
