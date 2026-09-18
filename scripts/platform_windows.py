"""Windows: register the native host with Google Chrome via the registry."""
import os
import shutil
import sys
import winreg
from pathlib import Path

LABEL = "Windows"
# Absolute interpreter path (forward slashes work in both Git Bash and cmd).
PYTHON = f'"{Path(sys.executable).as_posix()}"'
APP_DIR = Path(os.environ["LOCALAPPDATA"]) / "Claudication"
REG_KEY = r"Software\Google\Chrome\NativeMessagingHosts"


def register_host(root, host_name, manifest):
    # Chrome needs an executable, so a .bat launches the Python host.
    APP_DIR.mkdir(parents=True, exist_ok=True)
    bat = APP_DIR / "claudication_host.bat"
    with open(bat, "w", newline="\r\n") as f:
        f.write(f'@echo off\n"{sys.executable}" -u "{root / "host" / "claudication_host.py"}" %*\n')
    target = APP_DIR / f"{host_name}.json"
    target.write_text(manifest(str(bat)))
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"{REG_KEY}\{host_name}") as key:
        winreg.SetValueEx(key, "", 0, winreg.REG_SZ, str(target))
    return [str(target)]


def unregister_host(host_name):
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, rf"{REG_KEY}\{host_name}")
    except FileNotFoundError:
        pass
    shutil.rmtree(APP_DIR, ignore_errors=True)


def notifier_warning():
    return "If no toast appears, check Settings → System → Notifications and Focus assist."
