"""Desktop notifications with tools each OS already has: osascript, notify-send, PowerShell toasts."""
import os
import shutil
import subprocess
import sys

_QUIET = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}


def send(title, message, icon):
    """Show a notification without waiting for it, so the hook returns immediately."""
    if sys.platform == "darwin":
        _macos(title, message)
    elif sys.platform == "win32":
        _windows(title, message, icon)
    else:
        _linux(title, message, icon)


def setup_hint():
    """What the user may need to do before notifications appear, or None."""
    if sys.platform == "darwin":
        return "If none appear, allow notifications for Script Editor in System Settings → Notifications."
    if sys.platform == "win32":
        return "If none appear, check Settings → System → Notifications and Focus assist."
    if not shutil.which("notify-send"):
        return "notify-send not found. Install it with: sudo apt install libnotify-bin"
    return None


def _macos(title, message):
    # Values are passed as arguments, so quotes in a message can't break the script.
    script = [
        "on run argv",
        'display notification (item 2 of argv) with title "Claudication" subtitle (item 1 of argv) sound name "Glass"',
        "end run",
    ]
    args = ["osascript"]
    for line in script:
        args += ["-e", line]
    subprocess.Popen(args + [title, message], **_QUIET)


LINUX_SOUND = "/usr/share/sounds/freedesktop/stereo/complete.oga"


def _linux(title, message, icon):
    subprocess.Popen(["notify-send", "-a", "Claudication", "-i", str(icon), title, message], start_new_session=True, **_QUIET)
    if shutil.which("paplay"):
        subprocess.Popen(["paplay", LINUX_SOUND], start_new_session=True, **_QUIET)


# Registered app ID of Windows PowerShell; lets an unpackaged script raise toasts.
WINDOWS_APP_ID = r"{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe"

# Values arrive via environment variables and are XML-escaped, so a message can't inject markup.
WINDOWS_SCRIPT = r"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$t = [Security.SecurityElement]::Escape($env:CLAUDICATION_TITLE)
$m = [Security.SecurityElement]::Escape($env:CLAUDICATION_MESSAGE)
$i = [Security.SecurityElement]::Escape($env:CLAUDICATION_ICON)
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml("<toast><visual><binding template='ToastGeneric'><text>$t</text><text>$m</text><image placement='appLogoOverride' src='$i'/></binding></visual><audio src='ms-winsoundevent:Notification.Default'/></toast>")
$toast = New-Object Windows.UI.Notifications.ToastNotification $xml
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($env:CLAUDICATION_APP_ID).Show($toast)
"""

CREATE_NO_WINDOW = 0x08000000


def _windows(title, message, icon):
    env = dict(
        os.environ,
        CLAUDICATION_TITLE=title,
        CLAUDICATION_MESSAGE=message,
        CLAUDICATION_ICON=icon.as_uri(),
        CLAUDICATION_APP_ID=WINDOWS_APP_ID,
    )
    command = ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", WINDOWS_SCRIPT]
    subprocess.Popen(command, env=env, creationflags=CREATE_NO_WINDOW, **_QUIET)
