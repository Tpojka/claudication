"""macOS: register the native host with Google Chrome."""
import os
from pathlib import Path

LABEL = "macOS"
PYTHON = "python3"
HOST_DIR = Path.home() / "Library/Application Support/Google/Chrome/NativeMessagingHosts"


def register_host(root, host_name, manifest):
    host = root / "host" / "claudication_host.py"
    os.chmod(host, 0o755)
    HOST_DIR.mkdir(parents=True, exist_ok=True)
    target = HOST_DIR / f"{host_name}.json"
    target.write_text(manifest(str(host)))
    return [str(target)]


def unregister_host(host_name):
    (HOST_DIR / f"{host_name}.json").unlink(missing_ok=True)


def notifier_warning():
    return "Allow notifications for Script Editor in System Settings → Notifications if none appear."
