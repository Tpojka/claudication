#!/usr/bin/env python3
"""Add or remove Claudication hooks in ~/.claude/settings.json.

Used as a module by install.py. The CLI form from the first release still works:
    configure_hooks.py install <hook_script> | uninstall
"""
import json
import os
import shutil
import sys

SETTINGS = os.path.expanduser("~/.claude/settings.json")
MARKERS = ("claudication_hook.py", "claudication_notify.py")

# Claude Code hook event -> (matcher, state written by claudication_hook.py)
STATUS_EVENTS = {
    "SessionStart": (None, "ready"),
    "UserPromptSubmit": (None, "busy"),
    "PreToolUse": ("*", "busy"),
    "PostToolUse": ("*", "busy"),
    "Notification": ("permission_prompt|idle_prompt|elicitation_dialog", "ready"),
    "Stop": (None, "ready"),
    "SessionEnd": (None, "end"),
}

# Claude Code hook event -> (matcher, kind passed to claudication_notify.py)
NOTIFY_EVENTS = {
    "Stop": (None, "ready"),
    "Notification": ("permission_prompt|elicitation_dialog", "attention"),
}


def _is_ours(hook):
    return any(marker in hook.get("command", "") for marker in MARKERS)


def _strip_ours(hooks):
    for event in list(hooks):
        groups = []
        for group in hooks[event]:
            group["hooks"] = [h for h in group.get("hooks", []) if not _is_ours(h)]
            if group["hooks"]:
                groups.append(group)
        if groups:
            hooks[event] = groups
        else:
            del hooks[event]


def _add(hooks, events, python, script):
    for event, (matcher, arg) in events.items():
        group = {"hooks": [{"type": "command", "command": f'{python} "{script}" {arg}', "timeout": 5}]}
        if matcher:
            group["matcher"] = matcher
        hooks.setdefault(event, []).append(group)


def configure(python=None, status_script=None, notify_script=None):
    """Replace all Claudication hooks; with no scripts given, just remove them."""
    settings = {}
    if os.path.exists(SETTINGS):
        with open(SETTINGS, encoding="utf-8") as f:
            settings = json.load(f)
        shutil.copy2(SETTINGS, SETTINGS + ".claudication.bak")

    hooks = settings.setdefault("hooks", {})
    _strip_ours(hooks)
    if status_script:
        _add(hooks, STATUS_EVENTS, python, status_script)
    if notify_script:
        _add(hooks, NOTIFY_EVENTS, python, notify_script)
    if not hooks:
        del settings["hooks"]

    os.makedirs(os.path.dirname(SETTINGS), exist_ok=True)
    with open(SETTINGS, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    if sys.argv[1] == "install":
        configure("python3", sys.argv[2])
    else:
        configure()
