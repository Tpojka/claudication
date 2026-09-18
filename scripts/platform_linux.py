"""Ubuntu/Linux: register the native host with Google Chrome and Chromium."""
import os
import shutil
from pathlib import Path

LABEL = "Ubuntu/Linux"
PYTHON = "python3"
CONFIG = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
BROWSERS = ["google-chrome", "chromium"]


def _host_dirs():
    # Always Chrome; Chromium only when it has a profile.
    return [CONFIG / b / "NativeMessagingHosts" for b in BROWSERS if b == "google-chrome" or (CONFIG / b).is_dir()]


def register_host(root, host_name, manifest):
    host = root / "host" / "claudication_host.py"
    os.chmod(host, 0o755)
    written = []
    for d in _host_dirs():
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{host_name}.json").write_text(manifest(str(host)))
        written.append(str(d / f"{host_name}.json"))
    return written


def unregister_host(host_name):
    for b in BROWSERS:
        (CONFIG / b / "NativeMessagingHosts" / f"{host_name}.json").unlink(missing_ok=True)


def notifier_warning():
    if not shutil.which("notify-send"):
        return "notify-send not found. Install it with: sudo apt install libnotify-bin"
    return None
