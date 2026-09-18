"""Windows toast notifications via built-in PowerShell and the WinRT toast API."""
import os
import pathlib
import subprocess

# Registered app ID of Windows PowerShell; lets an unpackaged script raise toasts.
APP_ID = r"{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe"

# Values arrive via environment variables and are XML-escaped, so messages can't inject markup.
SCRIPT = r"""
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


def notify(title, message, icon):
    env = dict(
        os.environ,
        CLAUDICATION_TITLE=title,
        CLAUDICATION_MESSAGE=message,
        CLAUDICATION_ICON=pathlib.Path(icon).as_uri(),
        CLAUDICATION_APP_ID=APP_ID,
    )
    subprocess.Popen(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command", SCRIPT],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=CREATE_NO_WINDOW,
    )
