# Claude Code + iTerm2: Dynamic Tab Colors by State

Make your iTerm2 tabs change color based on what Claude Code is doing, so you can tell at a glance which sessions need your attention — especially handy when you have several Claude tabs open at once.

| State | Color | When |
|---|---|---|
| Working | 🔵 Blue | Claude is processing |
| Done | 🟢 Green | Idle, waiting for your next prompt |
| Needs input | 🔴 Red | Claude is about to run a `Write`, `Edit`, `Bash`, or `NotebookEdit` tool (held red while a permission prompt is open) |

The red state is approximated via `PreToolUse` because Claude Code does **not** emit `Notification` for in-CLI permission prompts when the tab is focused. So we color red whenever Claude is about to touch the filesystem or shell, and revert to blue when the tool completes. If you **deny** a tool, red persists until you submit your next prompt.

> The `Notification` hook is intentionally **not** wired — it fires on long-idle pings and produces spurious red states even when nothing needs attention.

## Prerequisites

- **macOS + iTerm2.**
- Set iTerm2 → **Settings → Appearance → General → Theme** to **Regular** or **Automatic**. The Minimal and Compact themes ignore terminal-set tab colors.
- **Claude Code** CLI installed.

## 1. Create the state script

Save the following as `~/.claude/state.sh`:

```bash
#!/usr/bin/env bash
# Set iTerm2 tab color based on Claude Code state.
# Usage: echo <working|done|input|reset> | ~/.claude/state.sh
#
# Hooks run without a controlling TTY, so we walk up the process tree until
# we find an ancestor with a real TTY (the iTerm2 session running Claude Code)
# and write the iTerm2 OSC 1337 SetColors escape sequence directly to it.

state=$(cat)
ESC=$'\033'
BEL=$'\a'

find_tty() {
  local pid=$PPID
  while [[ -n "$pid" && "$pid" != "0" && "$pid" != "1" ]]; do
    local t
    t=$(ps -o tty= -p "$pid" 2>/dev/null | tr -d ' ')
    if [[ -n "$t" && "$t" != "??" && "$t" != "-" ]]; then
      echo "/dev/$t"
      return
    fi
    pid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')
  done
}

tty_path=$(find_tty)
[[ -z "$tty_path" || ! -w "$tty_path" ]] && exit 0

emit() {
  printf '%s]1337;SetColors=%s%s' "$ESC" "$1" "$BEL" > "$tty_path"
}

case "$state" in
  working) emit "tab=0000ff" ;;  # blue
  done)    emit "tab=00c800" ;;  # green
  input)   emit "tab=c80000" ;;  # red
  reset)   emit "preset=Default" ;;
esac

exit 0
```

Make it executable:

```bash
chmod +x ~/.claude/state.sh
```

## 2. Wire up the Claude Code hooks

Edit `~/.claude/settings.json` and merge the following entries into the `hooks` object (don't overwrite any hooks you already have):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "echo working | ~/.claude/state.sh" }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          { "type": "command", "command": "echo working | ~/.claude/state.sh" }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          { "type": "command", "command": "echo done | ~/.claude/state.sh" }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Write|Edit|Bash|NotebookEdit",
        "hooks": [
          { "type": "command", "command": "echo input | ~/.claude/state.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit|Bash|NotebookEdit",
        "hooks": [
          { "type": "command", "command": "echo working | ~/.claude/state.sh" }
        ]
      }
    ]
  }
}
```

Validate the file:

```bash
jq . ~/.claude/settings.json > /dev/null && echo "valid"
```

> **Note:** Claude Code loads `settings.json` at session start. **Restart any open Claude sessions** after editing this file for the hooks to take effect.

## 3. Test it

In an iTerm2 tab, run each state manually — the tab should change color immediately:

```bash
echo working | ~/.claude/state.sh   # blue
echo done    | ~/.claude/state.sh   # green
echo input   | ~/.claude/state.sh   # red
echo reset   | ~/.claude/state.sh   # back to default
```

Then start a new Claude Code session and exercise it:

1. **Send a prompt** → tab turns blue.
2. **Wait for the response** → tab turns green when Claude finishes.
3. **Ask Claude to write a file or run a shell command** → tab flashes red when the tool is about to run. If a permission prompt appears, red holds until you respond.
4. **If you deny** the tool → red persists. It clears when you submit your next prompt.

## Behavior notes

- **Auto-approved tools flash red briefly** during the PreToolUse → PostToolUse window. Unavoidable with this approach; the flicker is short.
- **Allowlisted Bash commands** (in `permissions.allow`) still trigger PreToolUse, so they flash red too.

## Troubleshooting

**Manual test works, but hooks don't change the tab.**
Hook stdout is captured by Claude Code, so escape sequences printed to stdout never reach the terminal. The script above writes to the resolved TTY directly — make sure you copied the full version.

**`/dev/tty: Device not configured` error.**
Same root cause. Hooks have no controlling TTY; the script walks the process tree to find the iTerm2 session's TTY. Use the script above.

**Tab color never changes, even from a manual test in the terminal.**
Check the iTerm2 theme — Minimal and Compact ignore tab-color escapes. Switch to Regular or Automatic under Settings → Appearance → General.

**Tab doesn't go red on permission prompts.**
This was the original surprise: Claude Code's `Notification` hook does *not* fire for focused in-CLI permission prompts. The PreToolUse approach above is the workaround.

**Running over tmux/screen/SSH.**
Escape sequences don't pass through cleanly. tmux needs DCS-wrapping; SSH sessions can't reach the iTerm2 process on your laptop. This setup is designed for local iTerm2.

**Hook isn't firing at all.**
Run `/hooks` inside a Claude Code session — it lists registered hooks for that session. If yours aren't listed, your `settings.json` likely has a syntax error; re-run the `jq` check above. Remember: hooks are loaded at session start, so restart Claude after edits.

**Temporary diagnostic logging.**
Add this line near the top of `state.sh` to record every hook firing:
```bash
echo "$(date '+%H:%M:%S') state=$state tty=$tty_path iterm_id=${ITERM_SESSION_ID:-unset}" >> /tmp/claude-state.log
```
Then `tail -f /tmp/claude-state.log` while exercising Claude. Remove the line when done.

## Customizing colors

Change the hex codes in `state.sh`. iTerm2's OSC 1337 `SetColors` accepts any `RRGGBB`:

| Use | Hex |
|---|---|
| Bright blue | `1e90ff` |
| Soft green | `4caf50` |
| Amber (warning) | `ffa500` |
| Magenta | `c71585` |

## How it works

- **Hooks** in `~/.claude/settings.json` fire on Claude Code lifecycle events: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `Stop`.
- Each hook pipes a state keyword (`working` / `done` / `input`) into `state.sh`.
- The script walks up the process tree from the hook subprocess to find the iTerm2 session's TTY (`/dev/ttysNNN`) — necessary because hooks run without a controlling TTY.
- It writes an **iTerm2 OSC 1337 `SetColors`** escape sequence to that TTY. iTerm2 interprets that as "color this tab".

## Known limitations

- Red on focused permission prompts is only approximated via `PreToolUse` — meaning auto-approved tools also briefly flash red.
- Red persists after denying a tool until your next prompt (no hook fires on denial).
- Setup is local-only — escape sequences don't survive tmux, SSH, or Docker boundaries cleanly.
