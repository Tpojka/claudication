# Claudication

A Chrome toolbar button that shows whether Claude Code is working.

| Icon | Meaning |
| --- | --- |
| <img src="extension/icons/knee-pain-48.png" width="24"> | Knee in pain: Claude Code is working on a task |
| <img src="extension/icons/knee-ok-48.png" width="24"> | Knee without pain: Claude is ready (finished, or waiting for your input or permission) |
| <img src="extension/icons/knee-unknown-48.png" width="24"> | Grey: the native host isn't connected (run `install.sh`) |

Hover over the icon to see how many sessions are working.

## How it works

```
Claude Code hooks ──► ~/.claude/claudication/sessions/<session_id>  (busy | ready)
                                   │
             native messaging host (host/claudication_host.py) watches the files
                                   │  pushes status on change
                                   ▼
                  Chrome extension (extension/background.js) swaps the icon
```

- **Hooks** (`hooks/claudication_hook.py`): `UserPromptSubmit`, `PreToolUse` and `PostToolUse` mark the session busy. `Stop` and `Notification` (permission or idle prompts) mark it ready. `SessionEnd` removes it.
- **Multiple sessions**: the knee hurts while *any* session is busy.
- **Interrupts**: pressing Esc doesn't fire a `Stop` hook, so a session with no hook activity for 15 minutes counts as ready. Change this with `CLAUDICATION_BUSY_STALE_SECONDS` in the host's environment.

## Install (macOS, Google Chrome)

```sh
./install.sh
```

The script registers the native messaging host and adds the hooks to `~/.claude/settings.json`, keeping your existing hooks and writing a backup. Then:

1. Open `chrome://extensions` and turn on **Developer mode**.
2. Click **Load unpacked** and select the `extension/` folder.
3. Pin **Claudication** to the toolbar.
4. Restart any running Claude Code sessions so they load the hooks.

The manifest `key` gives the extension the fixed ID `hpoodlefheijkfkpebmooehgnjkibdnc`, which is the ID the native host allows.

Requires `python3`, which is `/usr/bin/python3` on macOS.

## Uninstall

```sh
./uninstall.sh
```

Then remove the extension from `chrome://extensions`.
