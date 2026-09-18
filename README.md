# Claudication — all platforms (macOS, Ubuntu, Windows)

A Chrome toolbar button that shows whether Claude Code is working, plus optional desktop notifications.

| Icon | Meaning |
| --- | --- |
| <img src="extension/icons/knee-pain-48.png" width="24"> | Knee in pain: Claude Code is working on a task |
| <img src="extension/icons/knee-ok-48.png" width="24"> | Knee without pain: Claude is ready (finished, or waiting for your input or permission) |
| <img src="extension/icons/knee-unknown-48.png" width="24"> | Grey: the native host isn't connected (run the installer) |

Hover over the icon to see how many sessions are working.

## Install

The installer detects your OS and uses the matching code. The `macos`, `ubuntu` and `windows` branches each contain only their own OS's code.

```sh
./install.sh        # macOS / Ubuntu
install.cmd         # Windows
```

The installer asks what to install:

```
  1) Chrome extension
  2) Chrome extension + notifier
  3) Nothing (exit)
```

You can also pass the choice directly, for example `install.py 2`. Running it again is safe: it replaces its own hooks, keeps any other hooks, and saves `~/.claude/settings.json.claudication.bak` first. Choosing option 1 after option 2 removes the notifier.

Then load the extension (only needed once):

1. Open `chrome://extensions` and turn on **Developer mode**.
2. Click **Load unpacked** and select the `extension/` folder.
3. Pin **Claudication** to the toolbar.
4. Restart any running Claude Code sessions so they load the hooks.

The manifest `key` gives the extension the same ID on every OS and every branch: `hpoodlefheijkfkpebmooehgnjkibdnc`.

Python 3 on every OS: macOS: `python3`, which is `/usr/bin/python3` on macOS; Ubuntu / Linux: `python3`; Windows: Python 3 from python.org or `winget install Python.Python.3.12`, available as `py` or `python`.

## Notifier

With option 2, you get a notification when Claude finishes a task (`Stop` hook) or needs your permission or input (`Notification` hook). The title includes the project folder name.

- **macOS:** macOS notifications through the built-in `osascript`, with the Glass sound. The first time, allow notifications for **Script Editor** in System Settings → Notifications.
- **Ubuntu / Linux:** Desktop notifications through `notify-send` (`sudo apt install libnotify-bin`), plus a sound through `paplay` if it's available.
- **Windows:** Windows toast notifications through built-in PowerShell. No modules are needed.

## Native host registration

- **macOS:** Google Chrome (`~/Library/Application Support/Google/Chrome/NativeMessagingHosts/`)
- **Ubuntu / Linux:** Google Chrome (`~/.config/google-chrome/NativeMessagingHosts/`) and Chromium (`~/.config/chromium/...`) if it has a profile. Snap and Flatpak browsers are sandboxed and can't start native hosts.
- **Windows:** Google Chrome (registry key `HKCU\Software\Google\Chrome\NativeMessagingHosts\com.tpojka.claudication`; the manifest and `.bat` launcher go in `%LOCALAPPDATA%\Claudication`)

## How it works

```
Claude Code hooks ──► ~/.claude/claudication/sessions/<session_id>  (busy | ready)
                                   │
             native messaging host (host/claudication_host.py) watches the files
                                   │  pushes status on change
                                   ▼
                  Chrome extension (extension/background.js) swaps the icon
```

- **Status hooks** (`hooks/claudication_hook.py`): `UserPromptSubmit`, `PreToolUse` and `PostToolUse` mark the session busy. `Stop` and `Notification` mark it ready. `SessionEnd` removes it.
- **Multiple sessions**: the knee hurts while *any* session is busy.
- **Interrupts**: pressing Esc doesn't fire a `Stop` hook, so a session with no hook activity for 15 minutes counts as ready. Change this with `CLAUDICATION_BUSY_STALE_SECONDS`.
- **Scope**: this covers Claude Code only (terminal, IDE extensions and the Desktop app's Code tab). It doesn't cover regular Claude chat.

## Uninstall

```sh
./uninstall.sh      # macOS / Ubuntu
uninstall.cmd       # Windows
```

Then remove the extension from `chrome://extensions`.

