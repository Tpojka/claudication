# Changelog

All notable changes to this project are documented here.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- MIT license.

## [2.1.0] - 2026-09-18

### Added

- **Optional notification sound.** When you choose the notifier, the installer asks `Play a sound with notifications? [Y/n]`. The answer is stored as `"sound"` in `config.json`. Without prompting: `python3 -m claudication.install 2 --no-sound`.
  *Why:* some people want the visual cue without the noise, and muting in the OS isn't obvious. On macOS, for example, the setting is under Script Editor.
  - macOS: leaves out `sound name "Glass"` from the notification.
  - Ubuntu/Linux: skips `paplay`, and passes the `suppress-sound` hint so desktops that add their own sound stay quiet.
  - Windows: sends `<audio silent='true'/>`. Leaving the audio element out entirely would still play Windows' default sound.
- **`set` command** to change settings after installing: `python3 -m claudication.install set sound|notifications on|off`.
  *Why:* the hook reads `config.json` on every event, so a setting can change without a reinstall. The command saves users from having to find the file on each OS.
- README section on the notifier settings: the terminal commands, `config.json`, and where to mute notifications in each OS's settings.

### Changed

- Menu option 2 is renamed from "Chrome extension + notifier" to "Chrome extension + OS notifier", to make clear the notifications come from the operating system rather than Chrome.

## [2.0.0] - 2026-09-18

A restructure for maintainability. What the extension does is unchanged, and it keeps the same extension ID. The install is not compatible with 1.x: run the new installer, then load the extension again from the new location (see **Upgrading from 1.x**).

### Changed

- **One branch for every OS.** The `macos`, `ubuntu`, `windows` and `all` branches are merged into `main`. The code detects the OS at runtime.
  *Why:* separate OS branches drift apart, and every fix had to be made up to four times. Only three small pieces differ between OSes (host registration, notifications, data location), and a few `sys.platform` checks cover them. The old branches remain available through their tags (see 1.1.0).
- **Installs outside the repository.** The installer copies everything into a per-user data directory: `~/Library/Application Support/Claudication` on macOS, `~/.local/share/claudication` on Linux and `%LOCALAPPDATA%\Claudication` on Windows. Chrome loads the extension from there.
  *Why:* in 1.x, the Claude Code hooks, the native host and the unpacked extension all pointed into the git checkout. Switching branches, pulling or moving the folder could break a working install, and a missing hook script makes Claude Code block tool calls. Now the repository is only a source.
- **Single app file.** The runtime code is packed into `claudication.pyz`, a zipapp that Python runs directly. Hooks run `claudication.pyz hook`, and Chrome's native host runs `claudication.pyz host` through a small launcher script.
  *Why:* one self-contained file is easy to copy, replace and remove, and it needs only the standard library.
- **One hook instead of two.** A single handler receives every event (Claude Code passes the event name in `hook_event_name`). It records the session state and, when the notifier is on, sends the notification. Whether notifications are on is stored in `config.json` in the data directory.
  *Why:* this halves the Python processes started per event. Turning the notifier on or off no longer rewrites `~/.claude/settings.json`, and the hook entries are identical for everyone.
- **Python package layout.** The flat `host/`, `hooks/` and `scripts/` folders are replaced by the `claudication` package, with one module per job: `hook`, `host`, `state`, `notify`, `config`, `paths` and `install`.
  *Why:* the hook and the host share the state logic in one module, where it was duplicated before. Every piece can be imported and tested on its own.
- **Installer entry point.** Run it with `python3 -m claudication.install`. `install.sh` and `install.cmd` are thin wrappers around it.
- **Idle reminders no longer notify.** Claude Code's "waiting for your input" reminder repeats the "Claude is ready" notification, so it no longer triggers one of its own.

### Added

- **Tests:** a `unittest` suite (standard library only) covers state aggregation, the hook, merging into Claude settings, the native messaging protocol, and a full install. The install test starts the registered host exactly as Chrome does.
- **CI:** GitHub Actions runs the tests on macOS, Ubuntu and Windows with Python 3.9 and the latest Python 3. This is the first time the Windows code runs on a real Windows machine.
- **`CLAUDICATION_HOME`:** overrides the data directory. The tests use it.
- This changelog.

### Removed

- The `macos`, `ubuntu`, `windows` and `all` branches. The `chrome-*-v1.1.0` tags still point to their final state.
- `host/`, `hooks/`, `scripts/` and the root `install.py`.

### Upgrading from 1.x

1. Run the new installer. It removes the 1.x hooks (recognised by their script names), replaces the native host registration and deletes the old state folder `~/.claude/claudication`.
2. In `chrome://extensions`, remove the old unpacked extension and load `extension` from the data directory. The installer prints the path.

## [1.1.0] - 2026-09-18

Tags: `chrome-all-os-v1.1.0`, `chrome-macos-v1.1.0`, `chrome-ubuntu-v1.1.0`, `chrome-windows-v1.1.0`.

### Added

- Ubuntu/Linux and Windows support, with separate branches per OS and an `all` branch that detects the OS.
- An optional notifier (macOS `osascript`, Linux `notify-send`, Windows PowerShell toast) for "Claude is ready" and "Claude needs you".
- An installer menu: Chrome extension, Chrome extension + notifier, or Nothing (exit).

## [1.0.0] - 2026-09-18

Tag: `chrome-extension-v1.0.0`.

### Added

- A Chrome extension whose toolbar icon shows a knee in pain while Claude Code works and a relaxed knee when Claude is ready.
- Claude Code hooks that record per-session state, and a native messaging host that pushes it to the extension.
- A macOS installer.

[Unreleased]: https://github.com/Tpojka/claudication/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/Tpojka/claudication/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/Tpojka/claudication/compare/chrome-all-os-v1.1.0...v2.0.0
[1.1.0]: https://github.com/Tpojka/claudication/compare/chrome-extension-v1.0.0...chrome-all-os-v1.1.0
[1.0.0]: https://github.com/Tpojka/claudication/releases/tag/chrome-extension-v1.0.0
