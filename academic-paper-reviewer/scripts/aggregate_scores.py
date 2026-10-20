#!/usr/bin/env python3
"""Aggregate reviewer scores into the Editorial Decision score summary.

Implements the arithmetic defined in references/quality_rubrics.md and
references/editorial_decision_standards.md so the Editorial Synthesizer does
not have to do weighted averages by hand:

  * confidence-weighted average of each 0-100 dimension across reviewers
  * spread (max - min) per dimension, flagged when > 20
  * composite score per reviewer and for the panel, using paper-type weights
  * suggested decision band from the composite
  * DA-CRITICAL cap (upheld critical issues cap the decision at 4 or 3)
  * consistency warnings when a reviewer's Overall (1-6) disagrees with the
    band implied by their own composite by 2 or more points
  * optional venue views (--venue / --all-venues): venue-emphasis weights,
    the venue's own score fields and scale, and a cross-venue outlook, using
    the profiles in scripts/venues.json

Usage:
    python3 scripts/aggregate_scores.py scores.json            # markdown
    python3 scripts/aggregate_scores.py scores.json --json     # machine-readable
    python3 scripts/aggregate_scores.py scores.json --venue cvpr --venue iclr
    python3 scripts/aggregate_scores.py scores.json --all-venues

Input format: see scripts/example_scores.json. Standard library only.
"""

import argparse
import json
import sys
from pathlib import Path

VENUES_FILE = Path(__file__).resolve().parent / "venues.json"

DIMENSIONS = [
    ("technical_rigor", "Technical Rigor"),
    ("clarity", "Clarity & Presentation"),
    ("novelty", "Novelty & Originality"),
    ("significance", "Significance & Impact"),
    ("experimental_validation", "Experimental Validation"),
    ("reproducibility", "Reproducibility"),
    ("ethics", "Ethical Compliance"),
]

# Order matches DIMENSIONS. Each row sums to 1.0 (checked at import time).
PAPER_TYPE_WEIGHTS = {
    "empirical":   [0.20, 0.10, 0.15, 0.15, 0.20, 0.10, 0.10],
    "theoretical": [0.30, 0.10, 0.20, 0.15, 0.10, 0.05, 0.10],
    "dataset":     [0.15, 0.10, 0.10, 0.20, 0.15, 0.15, 0.15],
    "system":      [0.20, 0.10, 0.10, 0.20, 0.20, 0.10, 0.10],
    "benchmark":   [0.15, 0.15, 0.10, 0.20, 0.20, 0.15, 0.05],
    "analysis":    [0.25, 0.10, 0.20, 0.20, 0.15, 0.05, 0.05],
    "position":    [0.15, 0.20, 0.25, 0.25, 0.05, 0.00, 0.10],
}
PAPER_TYPE_ALIASES = {
    "survey": "benchmark",
    "application": "system",
    "insight": "analysis",
    "vision": "position",
}
for _name, _w in PAPER_TYPE_WEIGHTS.items():
    assert abs(sum(_w) - 1.0) < 1e-9, _name

CONFIDENCE_WEIGHTS = {5: 1.00, 4: 0.85, 3: 0.70, 2: 0.55, 1: 0.40}

DECISIONS = {
    6: "Strong Accept",
    5: "Accept",
    4: "Borderline Accept",
    3: "Borderline Reject",
    2: "Reject",
    1: "Strong Reject",
}

HIGH_SPREAD = 20


def composite_to_overall(composite, offset=0):
    """Map a 0-100 composite to the 1-6 Overall band; offset raises the bar."""
    for threshold, band in ((85, 6), (70, 5), (60, 4), (50, 3), (35, 2)):
        if composite >= threshold + offset:
            return band
    return 1


def to_four(score):
    """0-100 dimension score -> NeurIPS-style 1-4 (references/quality_rubrics.md)."""
    if score >= 85:
        return 4
    if score >= 70:
        return 3
    if score >= 50:
        return 2
    return 1


def da_cap(da_critical):
    """Return (cap, reason) for upheld DA-CRITICAL issues, or (None, None)."""
    upheld = [i for i in da_critical if i.get("upheld", True)]
    if not upheld:
        return None, None
    resolvable = all(i.get("resolvable_without_new_data", False) for i in upheld)
    cap = 4 if resolvable else 3
    ids = ", ".join(i.get("id", "DA-C?") for i in upheld)
    reason = (f"{len(upheld)} upheld DA-CRITICAL issue(s) ({ids}); "
              f"cap = {cap} ({DECISIONS[cap]}) because "
              + ("all are resolvable by clarification or minor additions"
                 if resolvable else
                 "at least one needs new data, experiments, or redesign"))
    return cap, reason


def composite(scores, weights):
    return sum(scores[key] * w for (key, _), w in zip(DIMENSIONS, weights))


def fail(msg):
    sys.exit(f"error: {msg}")


def validate(data):
    if not isinstance(data.get("reviewers"), list) or not data["reviewers"]:
        fail("'reviewers' must be a non-empty list")
    for r in data["reviewers"]:
        role = r.get("role", "?")
        if r.get("confidence") not in CONFIDENCE_WEIGHTS:
            fail(f"reviewer {role}: confidence must be an integer 1-5")
        if "overall" in r and r["overall"] not in DECISIONS:
            fail(f"reviewer {role}: overall must be an integer 1-6")
        scores = r.get("scores", {})
        for key, label in DIMENSIONS:
            v = scores.get(key)
            if not isinstance(v, (int, float)) or not 0 <= v <= 100:
                fail(f"reviewer {role}: '{key}' ({label}) must be a number 0-100")


def aggregate(data):
    validate(data)
    paper_type = str(data.get("paper_type", "empirical")).lower()
    paper_type = PAPER_TYPE_ALIASES.get(paper_type, paper_type)
    if paper_type not in PAPER_TYPE_WEIGHTS:
        fail(f"unknown paper_type '{paper_type}'; "
             f"choose from {sorted(PAPER_TYPE_WEIGHTS)}")
    weights = PAPER_TYPE_WEIGHTS[paper_type]
    reviewers = data["reviewers"]
    cw = [CONFIDENCE_WEIGHTS[r["confidence"]] for r in reviewers]
    total_cw = sum(cw)

    dims = []
    for key, label in DIMENSIONS:
        vals = [r["scores"][key] for r in reviewers]
        avg = sum(v * w for v, w in zip(vals, cw)) / total_cw
        spread = max(vals) - min(vals)
        dims.append({
            "key": key,
            "label": label,
            "per_reviewer": vals,
            "weighted_avg": round(avg, 1),
            "spread": spread,
            "high_spread": spread > HIGH_SPREAD,
        })

    panel_scores = {d["key"]: d["weighted_avg"] for d in dims}
    panel_composite = round(composite(panel_scores, weights), 1)

    per_reviewer = []
    warnings = []
    for r in reviewers:
        c = round(composite(r["scores"], weights), 1)
        implied = composite_to_overall(c)
        entry = {"role": r.get("role", "?"), "composite": c,
                 "implied_overall": implied, "overall": r.get("overall")}
        per_reviewer.append(entry)
        if r.get("overall") is not None and abs(r["overall"] - implied) >= 2:
            warnings.append(
                f"{entry['role']}: Overall {r['overall']} vs. composite {c} "
                f"(implies {implied}). Re-check that scores match the text.")

    suggested = composite_to_overall(panel_composite)
    cap, cap_reason = da_cap(data.get("da_critical", []))
    capped = min(suggested, cap) if cap else suggested

    return {
        "paper_type": paper_type,
        "weights": dict(zip([k for k, _ in DIMENSIONS], weights)),
        "dimensions": dims,
        "panel_composite": panel_composite,
        "per_reviewer": per_reviewer,
        "suggested_overall": suggested,
        "final_overall_ceiling": capped,
        "decision_ceiling": DECISIONS[capped],
        "da_cap_reason": cap_reason,
        "warnings": warnings,
        "roles": [r.get("role", "?") for r in reviewers],
        "da_cap": cap,
    }


def load_venues(path=VENUES_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["venues"]


def venue_view(res, key, venue):
    """Re-score the panel's dimension averages through one venue's lens."""
    dims = {d["key"]: d["weighted_avg"] for d in res["dimensions"]}
    base = [res["weights"][k] for k, _ in DIMENSIONS]
    raw = [b * e for b, e in zip(base, venue["emphasis"])]
    weights = [w / sum(raw) for w in raw]
    comp = round(sum(dims[k] * w for (k, _), w in zip(DIMENSIONS, weights)), 1)
    offset = venue.get("bar_offset", 0)
    band = composite_to_overall(comp, offset)
    cap = res.get("da_cap")
    final = min(band, cap) if cap else band
    scale = venue["scale"]
    view = {"key": key, "name": venue["name"], "kind": venue["kind"],
            "as_of": venue["as_of"], "scale_status": scale["status"],
            "composite": comp, "bar_offset": offset, "band": band,
            "final": final, "subscores": {}, "notes": [scale["note"]]}

    for label, keys in venue.get("subscores", {}).items():
        view["subscores"][label] = to_four(sum(dims[k] for k in keys) / len(keys))

    if scale["type"] == "tmlr":
        evidence = (dims["technical_rigor"] + dims["experimental_validation"]
                    + dims["clarity"]) / 3
        audience = (dims["novelty"] + dims["significance"]) / 2
        claims_ok = evidence >= 60 and cap != 3
        view["subscores"]["Claims & evidence"] = "Yes" if claims_ok else "No"
        view["subscores"]["Audience interest"] = "Yes" if audience >= 40 else "No"
        if not claims_ok or audience < 40:
            view["label"] = "Reject (or major changes: narrow claims / add evidence)"
        elif cap == 4 or evidence < 70:
            view["label"] = "Accept with minor revision"
        else:
            view["label"] = "Accept"
    else:
        view["label"] = scale["map"][str(final)]
        if "legacy_map" in scale:
            view["label"] = (f"{view['label']} on {{0,2,4,6,8,10}} "
                             f"({scale['legacy_map'][str(final)]} on {{1,3,5,6,8,10}})")

    if key == "aaai" and final <= 3:
        view["notes"].append("Phase-1 early-rejection risk: "
                             + ("high" if final <= 2 else "moderate"))
    return view


def venue_markdown(views):
    lines = ["", "### Cross-Venue Outlook", "",
             "| Venue | Venue-weighted composite | Bar offset | Band before → after DA cap | "
             "Venue recommendation | Venue sub-scores | Scale status |",
             "|---|---|---|---|---|---|---|"]
    for v in views:
        subs = ", ".join(f"{k} {val}" for k, val in v["subscores"].items()) or "—"
        lines.append(f"| {v['name']} ({v['as_of']}) | {v['composite']} | "
                     f"{v['bar_offset']:+d} | {v['band']} → {v['final']} | {v['label']} | "
                     f"{subs} | {v['scale_status']} |")
    lines += ["", "Emphasis weights are this skill's heuristics, not official venue "
              "weights. Scale status: official / confirmed / secondary / assumed / unpublished "
              "(see references/venue_profiles.md). Upheld DA-CRITICAL caps apply to "
              "every venue.", ""]
    for v in views:
        for note in v["notes"]:
            lines.append(f"- **{v['name']}**: {note}")
    return "\n".join(lines)


def to_markdown(res):
    roles = res["roles"]
    lines = [f"**Paper type**: {res['paper_type']}  ",
             "**Weights**: " + ", ".join(
                 f"{label} {res['weights'][key]:.2f}" for key, label in DIMENSIONS),
             "",
             "| Dimension | " + " | ".join(roles) + " | Weighted Avg | Spread |",
             "|---" * (len(roles) + 3) + "|"]
    for d in res["dimensions"]:
        flag = " ⚠" if d["high_spread"] else ""
        vals = " | ".join(str(v) for v in d["per_reviewer"])
        lines.append(f"| {d['label']} | {vals} | {d['weighted_avg']} | "
                     f"{d['spread']}{flag} |")
    comps = " | ".join(str(p["composite"]) for p in res["per_reviewer"])
    lines.append(f"| **Composite** | {comps} | **{res['panel_composite']}** | |")
    lines.append("")
    lines.append("⚠ = spread > 20 points: discuss this disagreement in the decision.")
    lines.append("")
    lines.append(f"**Composite-implied decision**: {res['suggested_overall']} "
                 f"({DECISIONS[res['suggested_overall']]})  ")
    if res["da_cap_reason"]:
        lines.append(f"**DA-CRITICAL cap**: {res['da_cap_reason']}  ")
    lines.append(f"**Decision ceiling**: {res['final_overall_ceiling']} "
                 f"({res['decision_ceiling']}). The final decision may be lower "
                 "than this, never higher, and must be justified from review content.")
    if res["warnings"]:
        lines.append("")
        lines.append("**Consistency warnings**:")
        lines.extend(f"- {w}" for w in res["warnings"])
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("path", help="JSON file with reviewer scores ('-' for stdin)")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of markdown")
    ap.add_argument("--venue", action="append", default=[],
                    help="add a venue view (repeatable); see scripts/venues.json")
    ap.add_argument("--all-venues", action="store_true",
                    help="add views for every venue in scripts/venues.json")
    args = ap.parse_args()
    try:
        if args.path == "-":
            data = json.load(sys.stdin)
        else:
            with open(args.path, encoding="utf-8") as f:
                data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        fail(str(e))
    res = aggregate(data)
    keys = [k.lower() for k in args.venue + data.get("venues", [])]
    venues = load_venues() if (keys or args.all_venues) else {}
    if args.all_venues:
        keys = list(venues)
    for k in keys:
        if k not in venues:
            fail(f"unknown venue '{k}'; choose from {sorted(venues)}")
    views = [venue_view(res, k, venues[k]) for k in dict.fromkeys(keys)]
    if args.json:
        res["venue_views"] = views
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(to_markdown(res) + (venue_markdown(views) if views else ""))


if __name__ == "__main__":
    main()
