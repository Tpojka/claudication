"""Installer: copies the app and extension into the per-user data directory, then wires up Chrome and Claude Code.

Usage: python3 -m claudication.install              interactive menu
       python3 -m claudication.install 1|2|3        pick a menu option without prompting
       python3 -m claudication.install uninstall    remove everything
"""
import shutil
import sys
import tempfile
import zipapp
from pathlib import Path

from .. import __version__, config, notify, paths
from . import claude_settings, system

REPO = Path(__file__).resolve().parents[2]

MENU = """
Claudication {version} installer ({os})

  1) Chrome extension
  2) Chrome extension + notifier
  3) Nothing (exit)
"""


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    arg = argv[0] if argv else None
    if arg == "uninstall":
        uninstall()
        return
    choice = arg if arg in ("1", "2", "3") else ask()
    if choice == "3":
        print("Nothing installed.")
        return
    install(notifications=choice == "2")


def ask():
    print(MENU.format(version=__version__, os=system.label()))
    while True:
        try:
            choice = input("Choose 1, 2 or 3: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return "3"
        if choice in ("1", "2", "3"):
            return choice


def install(notifications):
    data = paths.data_dir()
    data.mkdir(parents=True, exist_ok=True)
    _remove_legacy_state()
    _copy_extension()
    app = _build_app()
    print(f"✓ Installed to {data}")

    for manifest in system.register_host(system.write_host_launcher(app)):
        print(f"✓ Native host registered: {manifest}")

    claude_settings.install(f'{system.python_command()} "{app.as_posix()}" hook')
    print(f"✓ Claude Code hooks added to {claude_settings.settings_path()} (backup: settings.json.claudication.bak)")

    config.save({"notifications": notifications})
    if notifications:
        print("✓ Notifier on: a notification appears when Claude finishes or needs you")
        hint = notify.setup_hint()
        if hint:
            print(f"  ! {hint}")
    else:
        print("✓ Notifier off")

    print(
        f"""
Next, if the extension isn't loaded yet: open chrome://extensions, turn on Developer mode,
click "Load unpacked" and pick: {paths.extension_dir()}
Then pin the knee to the toolbar. Restart running Claude Code sessions to load the hooks."""
    )


def uninstall():
    system.unregister_host()
    claude_settings.uninstall()
    shutil.rmtree(paths.data_dir(), ignore_errors=True)
    _remove_legacy_state()
    print("✓ Claudication removed. Remove the extension itself from chrome://extensions.")


def _remove_legacy_state():
    # 1.x kept session state here.
    shutil.rmtree(Path.home() / ".claude" / "claudication", ignore_errors=True)


def _copy_extension():
    # Chrome loads the unpacked extension from here, so the repository can be moved or deleted.
    target = paths.extension_dir()
    shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(REPO / "extension", target, ignore=shutil.ignore_patterns("*.svg", ".DS_Store"))


def _build_app():
    # Pack the runtime modules into one file that hooks and the native host run directly.
    target = paths.app_file()
    with tempfile.TemporaryDirectory() as staging:
        shutil.copytree(
            REPO / "claudication",
            Path(staging) / "claudication",
            ignore=shutil.ignore_patterns("__pycache__", "install"),
        )
        zipapp.create_archive(staging, target, main="claudication.cli:main")
    return target
