"""Adds and removes Claudication's hooks in ~/.claude/settings.json, leaving every other hook alone."""
import json
import os
import shutil

from ..hook import EVENTS

# Commands containing any of these belong to Claudication, including 1.x installs.
MARKERS = ("claudication.pyz", "claudication_hook.py", "claudication_notify.py")


def settings_path():
    return os.path.join(os.path.expanduser("~"), ".claude", "settings.json")


def install(command):
    """Register `command` for every event the hook handles, replacing any earlier Claudication hooks."""
    _update(command)


def uninstall():
    _update(None)


def _update(command):
    path = settings_path()
    settings = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            settings = json.load(f)
        shutil.copy2(path, path + ".claudication.bak")

    hooks = settings.setdefault("hooks", {})
    _remove_ours(hooks)
    if command:
        for event, (matcher, _) in EVENTS.items():
            group = {"hooks": [{"type": "command", "command": command, "timeout": 5}]}
            if matcher:
                group["matcher"] = matcher
            hooks.setdefault(event, []).append(group)
    if not hooks:
        del settings["hooks"]

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")


def _is_ours(hook):
    return any(marker in hook.get("command", "") for marker in MARKERS)


def _remove_ours(hooks):
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
