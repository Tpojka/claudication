"""Installer: copies the app and extension into the per-user data directory, then wires up Chrome and Claude Code.

Usage: python3 -m claudication.install                      interactive menu
       python3 -m claudication.install 1|2|3 [--no-sound]   pick a menu option without prompting
       python3 -m claudication.install set sound on|off     change a setting of the installed app
       python3 -m claudication.install set notifications on|off
       python3 -m claudication.install uninstall            remove everything
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
  2) Chrome extension + OS notifier
  3) Nothing (exit)
"""


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    arg = argv[0] if argv else None
    if arg == "uninstall":
        uninstall()
        return
    if arg == "set":
        set_option(*argv[1:3])
        return
    if arg in ("1", "2", "3"):
        choice, sound = arg, "--no-sound" not in argv
    else:
        choice = ask()
        sound = choice == "2" and ask_yes_no("Play a sound with notifications?")
    if choice == "3":
        print("Nothing installed.")
        return
    install(notifications=choice == "2", sound=sound)


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


def ask_yes_no(question):
    while True:
        try:
            answer = input(f"{question} [Y/n]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return True
        if answer in ("", "y", "yes"):
            return True
        if answer in ("n", "no"):
            return False


def set_option(name=None, value=None):
    """Change one setting in the installed config.json; the hook picks it up on its next event."""
    if name not in config.DEFAULTS or value not in ("on", "off"):
        sys.exit("usage: python3 -m claudication.install set sound|notifications on|off")
    if not paths.config_file().exists():
        sys.exit("Claudication isn't installed. Run the installer first.")
    settings = config.load()
    settings[name] = value == "on"
    config.save(settings)
    print(f"✓ {name.capitalize()} {value}")


def install(notifications, sound=True):
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

    config.save({"notifications": notifications, "sound": sound})
    if notifications:
        print(f"✓ OS notifier on, {'with' if sound else 'without'} sound: a notification appears when Claude finishes or needs you")
        hint = notify.setup_hint()
        if hint:
            print(f"  ! {hint}")
    else:
        print("✓ OS notifier off")

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
