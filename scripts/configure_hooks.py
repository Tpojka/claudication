#!/usr/bin/env python3
"""Add or remove Claudication hooks in ~/.claude/settings.json.

Usage: configure_hooks.py install <hook_script> | uninstall
"""
import json
import os
import shutil
import sys

SETTINGS = os.path.expanduser("~/.claude/settings.json")
MARKER = "claudication_hook.py"

# Claude Code hook event -> (matcher, state written by the hook)
EVENTS = {
    "SessionStart": (None, "ready"),
    "UserPromptSubmit": (None, "busy"),
    "PreToolUse": ("*", "busy"),
    "PostToolUse": ("*", "busy"),
    "Notification": ("permission_prompt|idle_prompt|elicitation_dialog", "ready"),
    "Stop": (None, "ready"),
    "SessionEnd": (None, "end"),
}


def strip_ours(hooks):
    for event in list(hooks):
        groups = []
        for group in hooks[event]:
            group["hooks"] = [h for h in group.get("hooks", []) if MARKER not in h.get("command", "")]
            if group["hooks"]:
                groups.append(group)
        if groups:
            hooks[event] = groups
        else:
            del hooks[event]


def main():
    mode = sys.argv[1]
    settings = {}
    if os.path.exists(SETTINGS):
        with open(SETTINGS) as f:
            settings = json.load(f)
        shutil.copy2(SETTINGS, SETTINGS + ".claudication.bak")

    hooks = settings.setdefault("hooks", {})
    strip_ours(hooks)

    if mode == "install":
        script = sys.argv[2]
        for event, (matcher, state) in EVENTS.items():
            group = {"hooks": [{"type": "command", "command": f'python3 "{script}" {state}', "timeout": 5}]}
            if matcher:
                group["matcher"] = matcher
            hooks.setdefault(event, []).append(group)

    if not hooks:
        del settings["hooks"]

    os.makedirs(os.path.dirname(SETTINGS), exist_ok=True)
    with open(SETTINGS, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
