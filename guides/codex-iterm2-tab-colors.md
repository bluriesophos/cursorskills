# Codex CLI + iTerm2: Dynamic Tab Colors by State

Make iTerm2 tabs change color based on what Codex is doing, so you can tell at a glance which sessions are working, idle, or blocked on a permission prompt.

This guide targets **Codex CLI 0.130.0** and installs into `~/.codex`, so it affects **all Codex sessions on the machine**, not just this repo.

| State | Color | When |
|---|---|---|
| Working | Blue | Codex is actively processing your prompt or running tools |
| Done | Green | Codex has finished the turn and is idle |
| Needs input | Red | Codex is waiting on a permission request |

## What Is Exact vs Approximate

Codex exposes a dedicated `PermissionRequest` hook, so the red permission state is exact.

Codex CLI 0.130.0 does **not** expose a separate hook for generic "the assistant asked a follow-up question and is now waiting for feedback." By default, this setup leaves those cases green rather than guessing.

There is an optional heuristic mode in the installed script if you want some stop states to turn red when the last assistant message looks like a question. It is off by default because false positives are worse than silence here.

Codex CLI 0.130.0 also requires two setup details that were not obvious up front:

- the working hook registration path is the global `~/.codex/config.toml` `[hooks]` table
- newly discovered hooks must be approved in `/hooks` before they become active

## Prerequisites

- **macOS + iTerm2**
- Set iTerm2 -> **Settings -> Appearance -> General -> Theme** to **Regular** or **Automatic**. The Minimal and Compact themes ignore terminal-set tab colors.
- **Codex CLI** installed

## 1. Install The Global Codex Hook

From this repo, run:

```bash
./guides/assets/codex-iterm2-tab-colors/install.sh
```

That installs:

- `~/.codex/codex-iterm2-tab-colors.sh`
- merged hook entries in `~/.codex/config.toml`

If you already have `~/.codex/config.toml`, the installer keeps it and writes a timestamped backup before merging.

## 2. What The Installer Adds

The checked-in config template is at:

- [`guides/assets/codex-iterm2-tab-colors/config.toml`](/Users/benjamin.lurie/development/cursorskills/guides/assets/codex-iterm2-tab-colors/config.toml)

It wires the same script to these Codex hook events:

- `SessionStart`
- `UserPromptSubmit`
- `PreToolUse`
- `PostToolUse`
- `PermissionRequest`
- `Stop`

The hook script is here:

- [`guides/assets/codex-iterm2-tab-colors/codex-iterm2-tab-colors.sh`](/Users/benjamin.lurie/development/cursorskills/guides/assets/codex-iterm2-tab-colors/codex-iterm2-tab-colors.sh)

It works like this:

- writes iTerm2 OSC 1337 color escapes directly to the terminal TTY
- keeps per-session state under `/private/tmp/codex-tab-color-state/`
- preserves red across a denied permission request by remembering whether the current turn ended while still blocked on approval

## 3. Restart Codex Sessions

Restart any open Codex sessions after installation so the new hooks load cleanly.

## 4. Approve The Hooks

After restart, open:

```text
/hooks
```

Codex will show the discovered hook handlers. Approve the six installed hooks so they move from review-pending to active.

## 5. Test It

Manual test from an iTerm2 tab:

```bash
~/.codex/codex-iterm2-tab-colors.sh manual working  # blue
~/.codex/codex-iterm2-tab-colors.sh manual done     # green
~/.codex/codex-iterm2-tab-colors.sh manual input    # red
~/.codex/codex-iterm2-tab-colors.sh manual reset    # default tab color
```

Then exercise Codex itself:

1. Submit a prompt -> tab turns blue.
2. Let Codex finish normally -> tab turns green.
3. Ask Codex to do something that requires approval -> tab turns red on the permission request.
4. Approve the request -> tab returns to blue while work continues, then green when the turn finishes.
5. Deny the request -> tab stays red until your next prompt.

## Optional: Heuristic Red For Some Follow-Up Questions

If you want the stop hook to turn red when the last assistant message looks like it is asking for feedback, enable this in the installed script:

- edit `~/.codex/codex-iterm2-tab-colors.sh`
- change `CODEX_TAB_COLOR_HEURISTIC_INPUT` from unset to `1`, for example by launching Codex with:

```bash
CODEX_TAB_COLOR_HEURISTIC_INPUT=1 codex
```

This is heuristic only. Common signoffs like "let me know if you want..." can create false reds, which is why it is off by default.

## Troubleshooting

**Manual test works, but Codex hooks do nothing.**

Check that `~/.codex/config.toml` contains the `[hooks]` entries, restart Codex, and confirm the hooks were approved in `/hooks`.

**The tab never changes color, even from the manual test.**

Check the iTerm2 theme. Minimal and Compact ignore terminal-set tab colors.

**The permission prompt turns red, but follow-up questions do not.**

That is the expected default. Codex currently exposes a dedicated permission hook, but not a first-class generic "waiting for user feedback" hook.

**The tab gets stuck red after something went wrong.**

Reset it manually:

```bash
~/.codex/codex-iterm2-tab-colors.sh manual reset
```

Then submit a new prompt to let the hook state resynchronize.

**Running under tmux, screen, or SSH.**

This setup is designed for local iTerm2 sessions. Escape sequences do not pass through those environments cleanly without extra wrapping.

## How It Works

- Codex hooks invoke a single shell script for lifecycle events.
- The hook registrations live in the global `~/.codex/config.toml` `[hooks]` table.
- Codex requires a one-time `/hooks` approval before newly discovered hooks become active.
- The script walks up the process tree to find the real iTerm2 TTY.
- It writes an iTerm2 OSC 1337 `SetColors` escape sequence directly to that TTY.
- A small per-session state file keeps permission-request turns red when a request is denied before tool execution continues.
