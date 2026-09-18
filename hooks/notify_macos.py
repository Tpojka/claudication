"""macOS notifications via the built-in osascript."""
import subprocess

# Values go in as arguments, so quotes in messages can't break the script.
SCRIPT = [
    "on run argv",
    'display notification (item 2 of argv) with title "Claudication" subtitle (item 1 of argv) sound name "Glass"',
    "end run",
]


def notify(title, message, icon):
    args = ["osascript"]
    for line in SCRIPT:
        args += ["-e", line]
    subprocess.Popen(args + [title, message], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
