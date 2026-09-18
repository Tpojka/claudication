#!/usr/bin/env python3
"""Claudication installer.

Usage: install.py              interactive menu
       install.py 1|2|3        pick a menu option without prompting
       install.py uninstall    remove everything
"""
import importlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
import configure_hooks  # noqa: E402

HOST_NAME = "com.tpojka.claudication"
EXTENSION_ID = "hpoodlefheijkfkpebmooehgnjkibdnc"  # fixed by the "key" in extension/manifest.json
STATE_DIR = Path.home() / ".claude" / "claudication"

# sys.platform -> (installer module, branch that carries it)
PLATFORMS = {
    "darwin": ("platform_macos", "macos"),
    "linux": ("platform_linux", "ubuntu"),
    "win32": ("platform_windows", "windows"),
}

MENU = """
Claudication installer ({label})

  1) Chrome extension
  2) Chrome extension + notifier
  3) Nothing (exit)
"""


def load_platform():
    if sys.platform not in PLATFORMS:
        sys.exit(f"Unsupported OS: {sys.platform}")
    module, branch = PLATFORMS[sys.platform]
    try:
        return importlib.import_module(module)
    except ModuleNotFoundError:
        sys.exit(f"This branch has no support for this OS. Check out the '{branch}' or 'all' branch.")


def manifest(host_path):
    return json.dumps(
        {
            "name": HOST_NAME,
            "description": "Claudication: Claude Code status for Chrome",
            "path": host_path,
            "type": "stdio",
            "allowed_origins": [f"chrome-extension://{EXTENSION_ID}/"],
        },
        indent=2,
    ) + "\n"


def ask(label):
    print(MENU.format(label=label))
    while True:
        try:
            choice = input("Choose 1, 2 or 3: ").strip()
        except (EOFError, KeyboardInterrupt):
            return "3"
        if choice in ("1", "2", "3"):
            return choice


def install(plat, with_notifier):
    for path in plat.register_host(ROOT, HOST_NAME, manifest):
        print(f"✓ Native host registered: {path}")

    notify = ROOT / "hooks" / "claudication_notify.py" if with_notifier else None
    configure_hooks.configure(plat.PYTHON, (ROOT / "hooks" / "claudication_hook.py").as_posix(), notify and notify.as_posix())
    print("✓ Claude Code status hooks added to ~/.claude/settings.json (backup: settings.json.claudication.bak)")
    if with_notifier:
        print("✓ Notifier hooks added: a notification appears when Claude finishes or needs you")
        warning = plat.notifier_warning()
        if warning:
            print(f"  ! {warning}")
    else:
        print("✓ Notifier not installed (any earlier notifier hooks were removed)")

    print(
        f"""
Next, if the extension isn't loaded yet: open chrome://extensions, turn on Developer mode,
click "Load unpacked" and pick: {ROOT / "extension"}
Then pin the knee to the toolbar. Restart running Claude Code sessions to load the hooks."""
    )


def uninstall(plat):
    plat.unregister_host(HOST_NAME)
    configure_hooks.configure()
    shutil.rmtree(STATE_DIR, ignore_errors=True)
    print("✓ Claudication removed. Remove the extension itself from chrome://extensions.")


def main():
    plat = load_platform()
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    if arg == "uninstall":
        return uninstall(plat)
    choice = arg if arg in ("1", "2", "3") else ask(plat.LABEL)
    if choice == "3":
        print("Nothing installed.")
        return
    install(plat, with_notifier=choice == "2")


if __name__ == "__main__":
    main()
