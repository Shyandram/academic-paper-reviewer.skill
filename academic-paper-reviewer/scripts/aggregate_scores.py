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
  * two score lists:
      OFFICIAL  - the reviewers' raw scores and their plain (unweighted) mean,
                  i.e. what the authors see; never modified
      EIC       - the EIC's internal assessment: each reviewer weighted by
                  confidence x the EIC's quality weight ("eic_weight", 0.5-1.5).
                  It can be higher or lower than OFFICIAL. The decision is
                  based on it, but it is not a revised official score.
  * the decision starting point is the EIC-weighted mean of the reviewers'
    Overall ratings (rounded half up); the 0-100 composite band is a
    cross-check, flagged when it disagrees
  * --final N renders venue labels from the EIC's actual decision
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
EIC_WEIGHT_RANGE = (0.5, 1.5)


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
        w = r.get("eic_weight", 1.0)
        if not isinstance(w, (int, float)) or not EIC_WEIGHT_RANGE[0] <= w <= EIC_WEIGHT_RANGE[1]:
            fail(f"reviewer {role}: eic_weight must be a number "
                 f"{EIC_WEIGHT_RANGE[0]}-{EIC_WEIGHT_RANGE[1]}")
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
    ew = [float(r.get("eic_weight", 1.0)) for r in reviewers]
    eic_weighted = any("eic_weight" in r for r in reviewers)
    combined = [c * e for c, e in zip(cw, ew)]

    def panel(rw):
        total = sum(rw)
        return {key: sum(r["scores"][key] * w for r, w in zip(reviewers, rw)) / total
                for key, _ in DIMENSIONS}

    before, after = panel([1.0] * len(reviewers)), panel(combined)
    dims = []
    for key, label in DIMENSIONS:
        vals = [r["scores"][key] for r in reviewers]
        spread = max(vals) - min(vals)
        dims.append({
            "key": key,
            "label": label,
            "per_reviewer": vals,
            "before_avg": round(before[key], 1),
            "weighted_avg": round(after[key], 1),
            "spread": spread,
            "high_spread": spread > HIGH_SPREAD,
        })

    before_composite = round(composite(before, weights), 1)
    panel_composite = round(composite(after, weights), 1)
    share = [w / sum(combined) for w in combined]

    per_reviewer = []
    warnings = []
    for r in reviewers:
        c = round(composite(r["scores"], weights), 1)
        implied = composite_to_overall(c)
        i = len(per_reviewer)
        entry = {"role": r.get("role", "?"), "composite": c,
                 "implied_overall": implied, "overall": r.get("overall"),
                 "confidence": r["confidence"], "confidence_weight": cw[i],
                 "eic_weight": ew[i], "weight_share": round(share[i], 3)}
        per_reviewer.append(entry)
        if r.get("overall") is not None and abs(r["overall"] - implied) >= 2:
            warnings.append(
                f"{entry['role']}: Overall {r['overall']} vs. composite {c} "
                f"(implies {implied}). Check that scores and text agree; "
                f"a deliberate gap is fine if the review explains it.")

    composite_band = composite_to_overall(panel_composite)
    overalls = [r.get("overall") for r in reviewers]
    if all(o is not None for o in overalls):
        official_rating = sum(overalls) / len(overalls)
        eic_rating = sum(o * w for o, w in zip(overalls, combined)) / sum(combined)
        suggested = max(1, min(6, int(eic_rating + 0.5)))   # round half up
        basis = "rating"
    else:   # fall back to the composite if any Overall rating is missing
        official_rating = eic_rating = None
        suggested = composite_band
        basis = "composite"
    cross_check = None
    if basis == "rating" and composite_band != suggested:
        cross_check = (f"Composite band {composite_band} ({DECISIONS[composite_band]}) differs from "
                       f"the rating-based starting point {suggested}. The EIC must say which "
                       f"signal it trusts and why.")
    cap, cap_reason = da_cap(data.get("da_critical", []))
    # The ceiling is the DA cap alone. The composite band is a guideline the
    # EIC may depart from (with a written reason); the cap is a hard limit.
    ceiling = cap if cap else 6

    return {
        "paper_type": paper_type,
        "weights": dict(zip([k for k, _ in DIMENSIONS], weights)),
        "dimensions": dims,
        "eic_weighted": eic_weighted,
        "before_composite": before_composite,     # OFFICIAL: plain mean of raw scores
        "before_overall": composite_to_overall(before_composite),
        "official_composite": before_composite,
        "eic_composite": panel_composite,
        "eic_minus_official": round(panel_composite - before_composite, 1),
        "panel_composite": panel_composite,
        "per_reviewer": per_reviewer,
        "suggested_overall": suggested,
        "suggestion_basis": basis,
        "official_rating": round(official_rating, 2) if official_rating is not None else None,
        "eic_rating": round(eic_rating, 2) if eic_rating is not None else None,
        "composite_band": composite_band,
        "cross_check": cross_check,
        "final_overall_ceiling": ceiling,
        "decision_ceiling": DECISIONS[ceiling],
        "da_cap_reason": cap_reason,
        "warnings": warnings,
        "roles": [r.get("role", "?") for r in reviewers],
        "da_cap": cap,
    }


def load_venues(path=VENUES_FILE):
    with open(path, encoding="utf-8") as f:
        return json.load(f)["venues"]


MIN_SHIFT_GAP = 2.0   # emphasis-only composite differences smaller than this are noise


def venue_view(res, key, venue, final=None, is_target=False):
    """Re-score the panel's dimension averages through one venue's lens."""
    dims = {d["key"]: d["weighted_avg"] for d in res["dimensions"]}
    base = [res["weights"][k] for k, _ in DIMENSIONS]
    raw = [b * e for b, e in zip(base, venue["emphasis"])]
    weights = [w / sum(raw) for w in raw]
    comp = round(sum(dims[k] * w for (k, _), w in zip(DIMENSIONS, weights)), 1)
    offset = venue.get("bar_offset", 0)
    # Venue adjustment: how much this venue's emphasis and bar move the
    # composite band relative to the default band, applied to the decision.
    shift = composite_to_overall(comp, offset) - res["composite_band"]
    if is_target:
        shift = 0   # the target venue's label always equals the EIC's decision
    elif offset == 0 and abs(comp - res["panel_composite"]) < MIN_SHIFT_GAP:
        shift = 0   # a band edge crossed by a tiny emphasis difference is not a venue effect
    start = final if final is not None else res["suggested_overall"]
    band = max(1, min(6, start + shift))
    cap = res.get("da_cap")
    final = min(band, cap) if cap else band
    scale = venue["scale"]
    view = {"key": key, "name": venue["name"], "kind": venue["kind"],
            "as_of": venue["as_of"], "scale_status": scale["status"],
            "composite": comp, "bar_offset": offset, "shift": shift, "band": band,
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
             "| Venue | Venue-weighted composite | Bar offset | Venue shift | Band → with DA cap | "
             "Venue recommendation | Venue sub-scores | Scale status |",
             "|---|---|---|---|---|---|---|---|"]
    for v in views:
        subs = ", ".join(f"{k} {val}" for k, val in v["subscores"].items()) or "—"
        lines.append(f"| {v['name']} ({v['as_of']}) | {v['composite']} | "
                     f"{v['bar_offset']:+d} | {v['shift']:+d} | {v['band']} → {v['final']} | {v['label']} | "
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
             "#### Reviewer weights (EIC, internal)",
             "",
             "| Reviewer | Confidence | Confidence weight | EIC quality weight | Share of EIC assessment |",
             "|---|---|---|---|---|"]
    for p in res["per_reviewer"]:
        lines.append(f"| {p['role']} | {p['confidence']} | {p['confidence_weight']:.2f} | "
                     f"{p['eic_weight']:.2f} | {p['weight_share']:.0%} |")
    if not res["eic_weighted"]:
        lines.append("")
        lines.append("*No EIC quality weights given yet: the EIC assessment uses confidence only. "
                     "Add `eic_weight` (0.5-1.5) per reviewer after the EIC's meta-review.*")
    lines += ["",
              "#### Official scores and EIC assessment",
              "",
              "| Dimension | " + " | ".join(roles) + " | Official (raw mean) | EIC assessment (weighted) | Spread |",
              "|---" * (len(roles) + 4) + "|"]
    for d in res["dimensions"]:
        flag = " ⚠" if d["high_spread"] else ""
        vals = " | ".join(str(v) for v in d["per_reviewer"])
        lines.append(f"| {d['label']} | {vals} | {d['before_avg']} | {d['weighted_avg']} | "
                     f"{d['spread']}{flag} |")
    comps = " | ".join(str(p["composite"]) for p in res["per_reviewer"])
    lines.append(f"| **Composite** | {comps} | **{res['before_composite']}** | "
                 f"**{res['panel_composite']}** | |")
    overalls = [(p["role"], p["overall"]) for p in res["per_reviewer"] if p["overall"] is not None]
    if overalls:
        lines += ["", "#### Ratings (the decision's starting point)", "",
                  "**Official reviewer ratings (Overall 1-6)**: "
                  + ", ".join(f"{r} {o}" for r, o in overalls)
                  + f" → official mean **{res['official_rating']:.2f}**  " if res["official_rating"] is not None else "",
                  f"**EIC-weighted rating** (internal): **{res['eic_rating']:.2f}** "
                  f"({res['eic_rating'] - res['official_rating']:+.2f} vs. official) → starting point "
                  f"**{res['suggested_overall']} ({DECISIONS[res['suggested_overall']]})**"
                  if res["eic_rating"] is not None else ""]
    lines += ["",
              "⚠ = spread > 20 points: discuss this disagreement in the decision.",
              "",
              "**Composite cross-check (0-100)**: "
              f"official {res['before_composite']} → {res['before_overall']} · "
              f"EIC-weighted {res['panel_composite']} → {res['composite_band']} "
              f"({res['eic_minus_official']:+.1f} vs. official)  "]
    if res["cross_check"]:
        lines.append(f"**⚠ Cross-check**: {res['cross_check']}  ")
    if res["da_cap_reason"]:
        lines.append(f"**DA-CRITICAL cap**: {res['da_cap_reason']}  ")
    lines.append(f"**Decision ceiling**: {res['final_overall_ceiling']} "
                 f"({res['decision_ceiling']}). The EIC's final decision may never exceed this. "
                 "It starts from the EIC-weighted rating and may depart from it in either direction, with a written reason.")
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
    ap.add_argument("--final", type=int, choices=range(1, 7), metavar="N",
                    help="the EIC's final Overall decision (1-6); venue labels are rendered from it")
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
    if args.final is not None:
        if args.final > res["final_overall_ceiling"]:
            fail(f"--final {args.final} exceeds the DA ceiling {res['final_overall_ceiling']}")
        res["final_overall"] = args.final
    ordered = list(dict.fromkeys(keys))
    target = ordered[0] if args.venue or data.get("venues") else None   # first --venue = target
    views = [venue_view(res, k, venues[k], args.final, is_target=(k == target)) for k in ordered]
    if args.json:
        res["venue_views"] = views
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(to_markdown(res) + (venue_markdown(views) if views else ""))


if __name__ == "__main__":
    main()
