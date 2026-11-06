#!/usr/bin/env bash
# Split pipeline for one paper: a fresh `claude -p` per phase (see run_split.py).
#
#   evals/split/run_paper.sh <paper id>
#
# PIPELINE=split (default): Phase 0, five parallel reviewers, check and EIC, each fresh.
# PIPELINE=check (skill 2.12 with its optional extensions): Phase 0 and the five reviewers
# in one context, the Gap Scout and the Report Checker each in a fresh context, then the
# first context resumed for the EIC. GAPS=0 skips the Gap Scout.
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
PIPELINE="${PIPELINE:-split}"; GAPS="${GAPS:-1}"
R="evals/work/results/$ID"; S="python3 -I evals/split/run_split.py"
ARGS=(--id "$ID" --lit "$LIT" --cutoff "$CUTOFF" --pipeline "$PIPELINE")
TOOLS=(Read Write Edit Glob Grep "Bash(python3:*)")
mkdir -p "$R"/{phase0,reports/{R1,R2,R3,R4,DA},gaps,check,eic,runs,prompts}

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

if [ "$PIPELINE" = check ]; then
  # Phase 0 and Phase 1 in one context, kept for the EIC.
  $S prompt panel "${ARGS[@]}" > "$R/prompts/panel.md"
  PERSIST=1 run panel "$R/prompts/panel.md" --allowedTools "${TOOLS[@]}"
  SID=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('session_id',''))" "$R/runs/panel.json" 2>/dev/null)
  [ -n "$SID" ] || { echo "panel: no session id"; exit 1; }
  $S before "${ARGS[@]}" || exit 1
  # Optional Gap Scout: a fresh context that reads the redacted copy only.
  if [ "$GAPS" = 1 ]; then
    $S prompt gaps "${ARGS[@]}" > "$R/prompts/gaps.md"
    mapfile -t GDENY < <($S deny --id "$ID" --role GAP)
    run gaps "$R/prompts/gaps.md" --allowedTools Read Write Glob Grep --disallowedTools Bash "${GDENY[@]}"
  fi
  # Optional Report Checker: a fresh context that did not write the reports.
  $S prompt check "${ARGS[@]}" > "$R/prompts/check.md"
  run check "$R/prompts/check.md" --allowedTools "${TOOLS[@]}" \
    --disallowedTools "Read(./evals/work/papers/**)" "Read(./$R/phase0/integrity.json)"
  # Phase 2 in the resumed panel context. The EIC never sees the Gap Scout list or the
  # checker's estimate.
  $S prompt eic --resumed "${ARGS[@]}" > "$R/prompts/eic.md"
  run eic "$R/prompts/eic.md" --resume "$SID" --allowedTools "${TOOLS[@]}" \
    --disallowedTools "Read(./$R/check/checker_estimate.json)" "Read(./$R/check/gaps_checked.md)" \
    "Read(./$R/gaps/**)"
  $S finish "${ARGS[@]}"
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
# Optional Gap Scout: a fresh context that reads the redacted copy only.
if [ "$GAPS" = 1 ]; then
  $S prompt gaps "${ARGS[@]}" > "$R/prompts/gaps.md"
  mapfile -t GDENY < <($S deny --id "$ID" --role GAP)
  run gaps "$R/prompts/gaps.md" --allowedTools Read Write Glob Grep --disallowedTools Bash "${GDENY[@]}"
fi
$S prompt check "${ARGS[@]}" > "$R/prompts/check.md"
run check "$R/prompts/check.md" --allowedTools "${TOOLS[@]}"
$S prompt eic "${ARGS[@]}" > "$R/prompts/eic.md"
run eic "$R/prompts/eic.md" --allowedTools "${TOOLS[@]}" \
  --disallowedTools "Read(./$R/check/checker_estimate.json)" "Read(./$R/check/gaps_checked.md)" \
  "Read(./$R/gaps/**)"
$S finish "${ARGS[@]}"
