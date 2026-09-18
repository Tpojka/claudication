#!/usr/bin/env python3
"""Claude Code hook: shows a desktop notification when Claude is ready or needs you.

Usage: claudication_notify.py ready|attention   (hook JSON arrives on stdin)
The platform backend (notify_macos / notify_linux / notify_windows) is picked at runtime.
"""
import importlib
import json
import os
import sys

BACKENDS = {"darwin": "notify_macos", "linux": "notify_linux", "win32": "notify_windows"}
ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "extension", "icons")


def main():
    kind = sys.argv[1] if len(sys.argv) > 1 else "ready"
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        payload = {}

    project = os.path.basename(os.path.normpath(payload.get("cwd") or os.getcwd()))
    if kind == "attention":
        title = "Claude needs you"
        message = payload.get("message") or "Claude is waiting for your input"
        icon = "knee-pain-128.png"
    else:
        title = "Claude is ready"
        message = "Task finished"
        icon = "knee-ok-128.png"

    backend = importlib.import_module(BACKENDS[sys.platform])
    backend.notify(f"{title} · {project}", message, os.path.join(ICON_DIR, icon))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # never block Claude Code
