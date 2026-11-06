#!/usr/bin/env bash
# Split pipeline for one paper: a fresh `claude -p` per phase (see run_split.py).
#
#   evals/split/run_paper.sh <paper id>
#
# PIPELINE=split (default): Phase 0, five parallel reviewers, check and EIC, each fresh.
# PIPELINE=check (skill 2.10.1): the review as in the single pipeline (Phase 0 and the five
# reviewers in one context, resumed for Phases 1.5, 1.6 and 2).
# Both then run the optional post-review analysis, each step in a fresh context that cannot
# change the review: the Report Checker's independent estimate (EST=0 skips it), the Gap
# Scout (GAPS=0 skips it) and the Report Checker's fact check (POST=0 skips it).
#
# Run from the repository root. Needs evals/work/papers/<id>/blinded.txt and an
# authenticated `claude` CLI: ANTHROPIC_API_KEY (API, billed per token) or
# CLAUDE_CODE_OAUTH_TOKEN / a local login (subscription, no API billing).
# Settings (environment): MODEL (default claude-sonnet-5-5), EFFORT (high),
# BUDGET (USD cap per phase, API only; 3), LIT (strict|on|off), CUTOFF,
# WARMUP (seconds between the first reviewer and the other four, so they read
# the shared prefix from the prompt cache; 20).
set -uo pipefail
ID="$1"
MODEL="${MODEL:-claude-sonnet-5-5}"; EFFORT="${EFFORT:-high}"; BUDGET="${BUDGET:-3}"
LIT="${LIT:-strict}"; CUTOFF="${CUTOFF:-}"; WARMUP="${WARMUP:-20}"
PIPELINE="${PIPELINE:-split}"; GAPS="${GAPS:-1}"; EST="${EST:-1}"; POST="${POST:-1}"
R="evals/work/results/$ID"; S="python3 -I evals/split/run_split.py"
ARGS=(--id "$ID" --lit "$LIT" --cutoff "$CUTOFF" --pipeline "$PIPELINE")
TOOLS=(Read Write Edit Glob Grep "Bash(python3:*)")
mkdir -p "$R"/{phase0,reports/{R1,R2,R3,R4,DA},gaps,check,eic,post,runs,prompts}

# run <name> <prompt file> [extra claude args...]: one context, its own run log.
# PERSIST=1 keeps the session so it can be resumed (`--resume <session id>` in the args).
run() {
  local name="$1" prompt="$2"; shift 2
  local t0; t0=$(date +%s)
  local keep=(--no-session-persistence); [ "${PERSIST:-0}" = 1 ] && keep=()
  claude -p "$(cat "$prompt")" --model "$MODEL" ${EFFORT:+--effort "$EFFORT"} \
    --max-budget-usd "$BUDGET" --output-format json "${keep[@]}" \
    --exclude-dynamic-system-prompt-sections "$@" > "$R/runs/$name.json" || true
  echo "{\"wall_s\": $(( $(date +%s) - t0 ))}" > "$R/runs/$name.wall.json"
  python3 -c "import json,sys;r=json.load(open(sys.argv[1]));print(sys.argv[2],'cost',r.get('total_cost_usd'),'turns',r.get('num_turns'),'error',r.get('is_error'))" \
    "$R/runs/$name.json" "$name" 2>/dev/null || echo "$name: no run log"
}

# post_review: optional analysis after the review is finished; it never changes the review.
post_review() {
  local deny=()
  if [ "$EST" = 1 ]; then   # from the redacted copy only, before seeing anything else
    $S prompt estimate "${ARGS[@]}" > "$R/prompts/estimate.md"
    mapfile -t deny < <($S deny --id "$ID" --role EST)
    run estimate "$R/prompts/estimate.md" --allowedTools Read Write Glob Grep --disallowedTools Bash "${deny[@]}"
  fi
  if [ "$GAPS" = 1 ]; then  # from the redacted copy only
    $S prompt gaps "${ARGS[@]}" > "$R/prompts/gaps.md"
    mapfile -t deny < <($S deny --id "$ID" --role GAP)
    run gaps "$R/prompts/gaps.md" --allowedTools Read Write Glob Grep --disallowedTools Bash "${deny[@]}"
  fi
  if [ "$POST" = 1 ]; then  # fact check of the finished review, and the Gap Scout list
    $S prompt post "${ARGS[@]}" > "$R/prompts/post.md"
    run post "$R/prompts/post.md" --allowedTools Read Write Glob Grep --disallowedTools Bash \
      "Read(./evals/work/papers/**)" "Read(./$R/phase0/integrity.json)" \
      "Edit(./$R/reports/**)" "Edit(./$R/check/**)" "Edit(./$R/eic/**)"   # Edit rules cover Write
  fi
  $S finish "${ARGS[@]}"   # again, to add the analysis to review.md and summary.json
}

if [ "$PIPELINE" = check ]; then
  # Phase 0 and Phase 1 in one context, kept for Phases 1.5, 1.6 and 2.
  $S prompt panel "${ARGS[@]}" > "$R/prompts/panel.md"
  PERSIST=1 run panel "$R/prompts/panel.md" --allowedTools "${TOOLS[@]}"
  SID=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('session_id',''))" "$R/runs/panel.json" 2>/dev/null)
  [ -n "$SID" ] || { echo "panel: no session id"; exit 1; }
  $S before "${ARGS[@]}" || exit 1
  $S prompt eic --resumed "${ARGS[@]}" > "$R/prompts/eic.md"
  run eic "$R/prompts/eic.md" --resume "$SID" --allowedTools "${TOOLS[@]}"
  $S finish "${ARGS[@]}"
  post_review
  exit
fi

# Phase 0: reads the unredacted paper, writes the redacted copy and the paper memory.
$S prompt phase0 "${ARGS[@]}" > "$R/prompts/phase0.md"
run phase0 "$R/prompts/phase0.md" --allowedTools "${TOOLS[@]}"
for f in card.md paper_memory.md panel.json reviewer_copy.txt; do
  [ -s "$R/phase0/$f" ] || { echo "phase0 did not write $f"; exit 1; }
done

# Phase 1: five reviewers, each in its own context, sharing one cached prefix.
$S shared "${ARGS[@]}" --out "$R/prompts/shared.md"
reviewer() {
  local role="$1"; local deny=()
  mapfile -t deny < <($S deny --id "$ID" --role "$role")
  $S prompt reviewer --role "$role" "${ARGS[@]}" > "$R/prompts/$role.md"
  run "$role" "$R/prompts/$role.md" --append-system-prompt-file "$R/prompts/shared.md" \
    --allowedTools Read Write Edit Glob Grep --disallowedTools Bash "${deny[@]}"
}
reviewer R1 & sleep "$WARMUP"
for role in R2 R3 R4 DA; do reviewer "$role" & done
wait
$S before "${ARGS[@]}" || exit 1

# Phase 1.5 + 1.6, then Phase 2, each fresh.
$S prompt check "${ARGS[@]}" > "$R/prompts/check.md"
run check "$R/prompts/check.md" --allowedTools "${TOOLS[@]}"
$S prompt eic "${ARGS[@]}" > "$R/prompts/eic.md"
run eic "$R/prompts/eic.md" --allowedTools "${TOOLS[@]}"
$S finish "${ARGS[@]}"
post_review
