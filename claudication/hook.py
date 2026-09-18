"""Claude Code hook: one handler for every event, recording state and sending notifications when enabled."""
import json
import os
import sys

from . import config, notify, paths, state

# Claude Code event -> (matcher to register with, state to record; None removes the session)
EVENTS = {
    "SessionStart": (None, state.READY),
    "UserPromptSubmit": (None, state.BUSY),
    "PreToolUse": ("*", state.BUSY),
    "PostToolUse": ("*", state.BUSY),
    "Notification": ("permission_prompt|idle_prompt|elicitation_dialog", state.READY),
    "Stop": (None, state.READY),
    "SessionEnd": (None, None),
}


def handle(payload):
    event = payload.get("hook_event_name")
    if event not in EVENTS:
        return
    session = str(payload.get("session_id") or "default")
    value = EVENTS[event][1]
    if value is None:
        state.clear(session)
    else:
        state.set_state(session, value)

    settings = config.load()
    if settings["notifications"]:
        message = notification_for(event, payload)
        if message:
            notify.send(*message, sound=settings["sound"])


def notification_for(event, payload):
    """Return (title, message, icon) for events worth a notification, else None."""
    project = os.path.basename(os.path.normpath(payload.get("cwd") or os.getcwd()))
    if event == "Stop":
        return f"Claude is ready · {project}", "Task finished", paths.icon("knee-ok")
    if event == "Notification" and not _is_idle_reminder(payload):
        message = payload.get("message") or "Claude is waiting for you"
        return f"Claude needs you · {project}", message, paths.icon("knee-pain")
    return None


def _is_idle_reminder(payload):
    # The idle reminder only repeats the Stop notification, so it gets none of its own.
    kind = payload.get("notification_type")
    if kind:
        return kind == "idle_prompt"
    return "waiting for your input" in (payload.get("message") or "")


def main():
    try:
        handle(json.load(sys.stdin))
    except Exception:
        pass  # a failing hook must never block Claude Code
