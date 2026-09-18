#!/usr/bin/env python3
"""Chrome native-messaging host for Claudication.

Watches the per-session state files written by the Claude Code hook and
pushes {"state": "busy"|"ready", "busy": n, "total": n} to the extension
whenever the aggregate status changes.
"""
import json
import os
import struct
import sys
import threading
import time

STATE_DIR = os.path.expanduser("~/.claude/claudication/sessions")
POLL_SECONDS = 0.5
# A session stuck "busy" with no hook activity for this long (e.g. the task was
# interrupted with Esc, which fires no Stop hook) is treated as ready.
BUSY_STALE_SECONDS = int(os.environ.get("CLAUDICATION_BUSY_STALE_SECONDS", 15 * 60))
# Sessions that vanished without a SessionEnd hook are dropped after this long.
SESSION_STALE_SECONDS = 24 * 60 * 60


def send(message):
    data = json.dumps(message).encode("utf-8")
    sys.stdout.buffer.write(struct.pack("@I", len(data)))
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()


def read_status():
    busy = total = 0
    now = time.time()
    try:
        names = os.listdir(STATE_DIR)
    except FileNotFoundError:
        names = []
    for name in names:
        if name.endswith(".tmp"):
            continue
        path = os.path.join(STATE_DIR, name)
        try:
            age = now - os.path.getmtime(path)
            with open(path) as f:
                state = f.read().strip()
        except OSError:
            continue
        if age > SESSION_STALE_SECONDS:
            continue
        total += 1
        if state == "busy" and age <= BUSY_STALE_SECONDS:
            busy += 1
    return {"state": "busy" if busy else "ready", "busy": busy, "total": total}


def watch_stdin():
    # Chrome closes stdin when the extension disconnects; exit with it.
    while sys.stdin.buffer.read(4096):
        pass
    os._exit(0)


def main():
    if sys.platform == "win32":
        import msvcrt
        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    threading.Thread(target=watch_stdin, daemon=True).start()
    last = None
    while True:
        status = read_status()
        if status != last:
            send(status)
            last = status
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()
