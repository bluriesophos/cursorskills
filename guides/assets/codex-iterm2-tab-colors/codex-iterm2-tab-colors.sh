#!/usr/bin/env bash
set -euo pipefail

CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
STATE_DIR="${CODEX_TAB_COLOR_STATE_DIR:-/private/tmp/codex-tab-color-state}"

ESC=$'\033'
BEL=$'\a'

mkdir -p "$STATE_DIR"

find_tty() {
  local pid="${PPID:-}"
  while [[ -n "${pid:-}" && "$pid" != "0" && "$pid" != "1" ]]; do
    local tty_name
    tty_name=$(ps -o tty= -p "$pid" 2>/dev/null | tr -d ' ')
    if [[ -n "$tty_name" && "$tty_name" != "??" && "$tty_name" != "-" ]]; then
      printf '/dev/%s\n' "$tty_name"
      return 0
    fi
    pid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')
  done
  return 1
}

emit_state() {
  local tty_path="$1"
  local state="$2"
  local payload=""

  case "$state" in
    working) payload="tab=0000ff" ;;
    done) payload="tab=00c800" ;;
    input) payload="tab=c80000" ;;
    reset) payload="preset=Default" ;;
    *) return 0 ;;
  esac

  [[ -w "$tty_path" ]] || return 0
  printf '%s]1337;SetColors=%s%s' "$ESC" "$payload" "$BEL" > "$tty_path"
}

json_field() {
  local field="$1"
  python3 -c '
import json
import sys

field = sys.argv[1]
try:
    payload = json.load(sys.stdin)
except Exception:
    sys.exit(1)

value = payload.get(field)
if value is None:
    sys.exit(0)
if isinstance(value, bool):
    print("true" if value else "false")
elif isinstance(value, (dict, list)):
    print(json.dumps(value, separators=(",", ":")))
else:
    print(str(value))
' "$field"
}

should_mark_input_from_message() {
  local message="$1"
  [[ "${CODEX_TAB_COLOR_HEURISTIC_INPUT:-0}" == "1" ]] || return 1
  [[ -n "$message" ]] || return 1

  python3 - "$message" <<'PY'
import re
import sys

message = sys.argv[1].strip().lower()
patterns = [
    r"\?$",
    r"\bdo you want\b",
    r"\bwould you like\b",
    r"\bwhich\b",
    r"\bcan you\b",
    r"\bcould you\b",
    r"\bplease review\b",
    r"\blet me know\b",
]
sys.exit(0 if any(re.search(pattern, message) for pattern in patterns) else 1)
PY
}

write_session_state() {
  local session_id="$1"
  local turn_id="$2"
  local state="$3"
  printf '%s\t%s\n' "$turn_id" "$state" > "$STATE_DIR/$session_id"
}

read_session_state() {
  local session_id="$1"
  local state_file="$STATE_DIR/$session_id"
  if [[ -f "$state_file" ]]; then
    cat "$state_file"
  fi
}

handle_manual() {
  local tty_path
  tty_path=$(find_tty || true)
  [[ -n "${tty_path:-}" ]] || exit 0
  emit_state "$tty_path" "${2:-}"
}

if [[ "${1:-}" == "manual" ]]; then
  handle_manual "$@"
  exit 0
fi

payload=$(cat)
[[ -n "$payload" ]] || exit 0

hook_event_name=$(printf '%s' "$payload" | json_field "hook_event_name" || true)
session_id=$(printf '%s' "$payload" | json_field "session_id" || true)
turn_id=$(printf '%s' "$payload" | json_field "turn_id" || true)
last_assistant_message=$(printf '%s' "$payload" | json_field "last_assistant_message" || true)

tty_path=$(find_tty || true)
[[ -n "${tty_path:-}" ]] || exit 0

case "$hook_event_name" in
  SessionStart)
    write_session_state "$session_id" "$turn_id" "done"
    emit_state "$tty_path" "done"
    ;;
  UserPromptSubmit)
    write_session_state "$session_id" "$turn_id" "working"
    emit_state "$tty_path" "working"
    ;;
  PreToolUse|PostToolUse)
    write_session_state "$session_id" "$turn_id" "working"
    emit_state "$tty_path" "working"
    ;;
  PermissionRequest)
    write_session_state "$session_id" "$turn_id" "input"
    emit_state "$tty_path" "input"
    ;;
  Stop)
    prior_state=$(read_session_state "$session_id" || true)
    prior_turn_id="${prior_state%%$'\t'*}"
    prior_mode="${prior_state#*$'\t'}"

    if [[ "$prior_turn_id" == "$turn_id" && "$prior_mode" == "input" ]]; then
      emit_state "$tty_path" "input"
      exit 0
    fi

    if should_mark_input_from_message "${last_assistant_message:-}"; then
      write_session_state "$session_id" "$turn_id" "input"
      emit_state "$tty_path" "input"
    else
      write_session_state "$session_id" "$turn_id" "done"
      emit_state "$tty_path" "done"
    fi
    ;;
esac

exit 0
