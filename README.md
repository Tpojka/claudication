# Claudication

A Chrome toolbar button that shows whether Claude Code is working, with optional desktop notifications. It works on macOS, Ubuntu/Linux and Windows.

| Icon | Meaning |
| --- | --- |
| <img src="extension/icons/knee-pain-48.png" width="24"> | Knee in pain: Claude Code is working on a task |
| <img src="extension/icons/knee-ok-48.png" width="24"> | Knee without pain: Claude is ready (finished, or waiting for your input or permission) |
| <img src="extension/icons/knee-unknown-48.png" width="24"> | Grey: the native host isn't connected (run the installer) |

Hover over the icon to see how many sessions are working.

## Install

Requires Python 3.9 or newer. macOS ships it as `/usr/bin/python3`. On Windows, install it from python.org or with `winget install Python.Python.3.12`.

```sh
./install.sh        # macOS / Ubuntu
install.cmd         # Windows
```

The installer detects your OS and asks what to install:

```
  1) Chrome extension
  2) Chrome extension + notifier
  3) Nothing (exit)
```

To skip the prompt, pass the choice directly: `python3 -m claudication.install 2`.

Everything is copied into a per-user data directory, so you can move or delete the repository afterwards:

| OS | Data directory |
| --- | --- |
| macOS | `~/Library/Application Support/Claudication` |
| Ubuntu/Linux | `~/.local/share/claudication` (or `$XDG_DATA_HOME/claudication`) |
| Windows | `%LOCALAPPDATA%\Claudication` |

Then load the extension from that directory (only needed once):

1. Open `chrome://extensions` and turn on **Developer mode**.
2. Click **Load unpacked** and select the `extension` folder inside the data directory. The installer prints the exact path.
3. Pin **Claudication** to the toolbar.
4. Restart any running Claude Code sessions so they load the hooks.

Running the installer again is safe. It updates the installed copy and replaces its own hooks, leaves your other hooks alone, and backs up `~/.claude/settings.json` to `settings.json.claudication.bak` first. To turn the notifier on or off, run it again and choose 2 or 1.

## Notifier

When the notifier is on, you get a notification when Claude finishes a task or needs your permission or input. The title includes the project folder name.

- **macOS:** built-in `osascript`, with the Glass sound. The first time, allow notifications for **Script Editor** in System Settings → Notifications.
- **Ubuntu/Linux:** `notify-send` (`sudo apt install libnotify-bin`), plus a sound through `paplay` when available.
- **Windows:** a toast through built-in PowerShell. No modules are needed.

## How it works

```
Claude Code ──hook──► claudication.pyz hook ──► <data>/sessions/<session_id>   (busy | ready)
                                  └──────────► desktop notification (if enabled)

Chrome ──starts──► claudication-host ──► claudication.pyz host
                      watches <data>/sessions, pushes status on change
                                  │  native messaging
                                  ▼
                   extension/background.js swaps the icon
```

- **One hook for every event.** Claude Code runs `claudication.pyz hook` and passes the event name on stdin. `UserPromptSubmit`, `PreToolUse` and `PostToolUse` mark the session busy. `Stop` and `Notification` mark it ready. `SessionEnd` removes it.
- **Multiple sessions:** the knee hurts while *any* session is busy.
- **Interrupts:** pressing Esc fires no `Stop` hook, so a session with no hook activity for 15 minutes counts as ready. Change this with `CLAUDICATION_BUSY_STALE_SECONDS`.
- **Scope:** Claude Code only (terminal, IDE extensions and the Desktop app's Code tab). It doesn't cover regular Claude chat.
- **Stable extension ID:** the `key` in `extension/manifest.json` fixes the ID to `hpoodlefheijkfkpebmooehgnjkibdnc`, which is the only extension the native host accepts.

## Project layout

```
claudication/          Python package (standard library only)
  hook.py              Claude Code hook handler
  host.py              Chrome native messaging host
  state.py             per-session busy/ready files
  notify.py            desktop notifications per OS
  config.py, paths.py  installed settings and locations
  cli.py               entry point of the installed claudication.pyz
  install/             installer: copies files, registers the host, edits Claude settings
extension/             Chrome extension (Manifest V3)
tests/                 unittest suite
```

## Development

```sh
python3 -m unittest -v
```

The tests are self-contained. Every test uses a temporary home and data directory, so your real install isn't touched. CI runs them on macOS, Ubuntu and Windows with Python 3.9 and the latest Python 3.

To use a data directory other than the default, set `CLAUDICATION_HOME`.

## Uninstall

```sh
./uninstall.sh      # macOS / Ubuntu
uninstall.cmd       # Windows
```

This removes the hooks, the native host registration and the data directory. Then remove the extension from `chrome://extensions`.

See [CHANGELOG.md](CHANGELOG.md) for release history.
