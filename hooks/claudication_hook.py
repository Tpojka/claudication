#!/usr/bin/env python3
"""Claude Code hook: records this session's state for the Claudication extension.

Usage: claudication_hook.py busy|ready|end   (hook JSON arrives on stdin)
"""
import json
import os
import sys

STATE_DIR = os.path.expanduser("~/.claude/claudication/sessions")


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "ready"
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        payload = {}
    session = "".join(c for c in str(payload.get("session_id", "default")) if c.isalnum() or c in "-_")
    path = os.path.join(STATE_DIR, session or "default")

    if action == "end":
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        return

    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        f.write(action)
    os.replace(tmp, path)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # never block Claude Code
