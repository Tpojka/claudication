"""Linux notifications via notify-send (Ubuntu package: libnotify-bin)."""
import shutil
import subprocess

SOUND = "/usr/share/sounds/freedesktop/stereo/complete.oga"


def notify(title, message, icon):
    quiet = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL, "start_new_session": True}
    subprocess.Popen(["notify-send", "-a", "Claudication", "-i", icon, title, message], **quiet)
    if shutil.which("paplay"):
        subprocess.Popen(["paplay", SOUND], **quiet)
