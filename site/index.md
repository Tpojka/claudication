# Claudication

> **Archived.** Claudication is now part of [Perturbation](https://perturbation.tpojka.com), one Chrome toolbar lamp for Claude Code, Codex CLI, GitHub Copilot CLI, Antigravity CLI, opencode, Goose and Qwen Code. Its installer finds Claudication and offers to remove it: <https://perturbation.tpojka.com>

**Your knee hurts while Claude works. It relaxes when Claude is ready.**

A Chrome toolbar button that shows whether Claude Code is working, with optional desktop notifications. It works on macOS, Ubuntu and Windows.

> *claudication* (n.): pain in the legs that comes on while they're working and eases with rest.

- Website: <https://claudication.tpojka.com>
- Source: <https://github.com/Tpojka/claudication>

---

## Three states, one glance

| Icon | State | Meaning |
| :-: | --- | --- |
| 🔴 | **Working** | Claude Code is working on a task in at least one session |
| 🟢 | **Ready** | Claude has finished, or is waiting for your input or permission |
| ⚪ | **Not connected** | The local helper isn't running. Run the installer |

Hover over the icon to see how many sessions are working.

## What you get

- **Live toolbar status:** the icon changes the moment Claude starts or finishes, with no polling delay.
- **Every session:** the knee hurts while *any* Claude Code session is working.
- **OS notifications:** optional alerts when Claude finishes or needs your permission, with or without sound.
- **Three platforms:** macOS, Ubuntu/Linux and Windows. The installer detects which one you're on.
- **Stays out of the way:** it installs into your user data folder and leaves your other Claude Code hooks alone.
- **Fully local:** nothing leaves your machine. The status goes from Claude Code hooks to Chrome over native messaging.

## Install

Requires Python 3.9 or newer and Google Chrome.

**macOS**

```sh
git clone https://github.com/Tpojka/claudication.git
cd claudication
./install.sh
```

**Ubuntu**

```sh
sudo apt install python3 libnotify-bin   # notify-send, for the notifier
git clone https://github.com/Tpojka/claudication.git
cd claudication
./install.sh
```

**Windows**

```bat
winget install Python.Python.3.12
git clone https://github.com/Tpojka/claudication.git
cd claudication
install.cmd
```

The installer asks:

```
  1) Chrome extension
  2) Chrome extension + OS notifier
  3) Nothing (exit)
Choose 1, 2 or 3: 2
Play a sound with notifications? [Y/n]:
```

Then load the extension (once):

1. Open `chrome://extensions` and turn on **Developer mode**.
2. Click **Load unpacked** and pick the `extension` folder the installer printed.
3. Pin **Claudication** to the toolbar.
4. Restart any running Claude Code sessions so they load the hooks.

## OS notifier

You get a notification when Claude finishes a task or needs your permission. The title includes the project name.

Change the settings any time from the repository. They take effect with the next notification, with no restart:

```sh
python3 -m claudication.install set sound off           # silent notifications
python3 -m claudication.install set sound on
python3 -m claudication.install set notifications off   # no notifications at all
python3 -m claudication.install set notifications on
```

On Windows, use `py -3` instead of `python3`.

Or use your OS settings:

| OS | Where |
| --- | --- |
| macOS | System Settings → Notifications → **Script Editor** |
| Ubuntu (GNOME) | Settings → Sound → **System Sounds**, or Notifications → Do Not Disturb |
| Windows | Settings → System → Notifications → **Windows PowerShell** |

## How it works

```
Claude Code ──hook──► claudication.pyz hook ──► sessions/<id>   (busy | ready)
                                  └──────────► desktop notification (optional)

Chrome ──starts──► claudication.pyz host
                      watches sessions/, pushes status on change
                                  │  native messaging
                                  ▼
                   extension swaps the icon
```

It covers **Claude Code**: the terminal, IDE extensions and the Desktop app's Code tab. It doesn't cover regular Claude chat.

---

Claudication 2.1.0 · [MIT](https://github.com/Tpojka/claudication/blob/main/LICENSE) © 2026 Goran Grbic · An independent project, not affiliated with Anthropic.

Archived in favor of [Perturbation](https://perturbation.tpojka.com).
