#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
TARGET_SCRIPT="$CODEX_HOME/codex-iterm2-tab-colors.sh"
TARGET_CONFIG="$CODEX_HOME/config.toml"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"

mkdir -p "$CODEX_HOME"
cp "$SCRIPT_DIR/codex-iterm2-tab-colors.sh" "$TARGET_SCRIPT"
chmod +x "$TARGET_SCRIPT"

if [[ -f "$TARGET_CONFIG" ]]; then
  cp "$TARGET_CONFIG" "$TARGET_CONFIG.bak.$TIMESTAMP"
fi

python3 - "$TARGET_CONFIG" "$TARGET_SCRIPT" <<'PY'
import os
import sys
import tomllib

config_path = sys.argv[1]
script_path = sys.argv[2]

events = [
    "SessionStart",
    "UserPromptSubmit",
    "PreToolUse",
    "PostToolUse",
    "PermissionRequest",
    "Stop",
]

existing = ""
if os.path.exists(config_path):
    existing = open(config_path, "r", encoding="utf-8").read()
    try:
        parsed = tomllib.loads(existing)
    except Exception as exc:
        raise SystemExit(f"Existing config.toml is not valid TOML: {exc}")
    hooks = parsed.get("hooks")
    if hooks is not None and not isinstance(hooks, dict):
        raise SystemExit("Existing config.toml has a non-table 'hooks' value.")

block_lines = ["", "[hooks]"]
for event in events:
    block_lines.append(f'{event} = [')
    block_lines.append(f'  {{ hooks = [ {{ type = "command", command = "{script_path}", async = false }} ] }}')
    block_lines.append(']')
block = "\n".join(block_lines) + "\n"

if "[hooks]" not in existing:
    output = existing.rstrip() + block + "\n" if existing.strip() else block.lstrip("\n")
else:
    output = existing
    for event in events:
        header = f"{event} = ["
        if header in output:
            continue
        insertion = (
            f'{event} = [\n'
            f'  {{ hooks = [ {{ type = "command", command = "{script_path}", async = false }} ] }}\n'
            f']\n'
        )
        output += "\n" + insertion

with open(config_path, "w", encoding="utf-8") as f:
    f.write(output)
PY

printf 'Installed %s\n' "$TARGET_SCRIPT"
printf 'Updated %s\n' "$TARGET_CONFIG"
if [[ -f "$TARGET_CONFIG.bak.$TIMESTAMP" ]]; then
  printf 'Backup saved to %s\n' "$TARGET_CONFIG.bak.$TIMESTAMP"
fi
