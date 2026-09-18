import json
import os

from claudication.hook import EVENTS
from claudication.install import claude_settings
from tests.support import IsolatedTestCase

COMMAND = 'python3 "/data/claudication.pyz" hook'
FOREIGN = {"type": "command", "command": "say done"}
LEGACY = {"type": "command", "command": 'python3 "/repo/hooks/claudication_hook.py" ready'}


class ClaudeSettingsTest(IsolatedTestCase):
    def write(self, settings):
        path = claude_settings.settings_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(settings, f)

    def read(self):
        with open(claude_settings.settings_path()) as f:
            return json.load(f)

    def commands(self, event):
        return [h["command"] for g in self.read()["hooks"].get(event, []) for h in g["hooks"]]

    def test_registers_every_event(self):
        claude_settings.install(COMMAND)
        self.assertEqual(set(self.read()["hooks"]), set(EVENTS))
        self.assertEqual(self.read()["hooks"]["PreToolUse"][0]["matcher"], "*")

    def test_keeps_other_settings_and_hooks(self):
        self.write({"model": "opus", "hooks": {"Stop": [{"hooks": [FOREIGN]}]}})
        claude_settings.install(COMMAND)
        self.assertEqual(self.read()["model"], "opus")
        self.assertEqual(self.commands("Stop"), ["say done", COMMAND])

    def test_reinstall_does_not_duplicate(self):
        claude_settings.install(COMMAND)
        claude_settings.install(COMMAND)
        self.assertEqual(self.commands("Stop"), [COMMAND])

    def test_replaces_legacy_hooks(self):
        self.write({"hooks": {"Stop": [{"hooks": [LEGACY]}]}})
        claude_settings.install(COMMAND)
        self.assertEqual(self.commands("Stop"), [COMMAND])

    def test_uninstall_removes_only_ours(self):
        self.write({"hooks": {"Stop": [{"hooks": [FOREIGN, LEGACY]}]}})
        claude_settings.install(COMMAND)
        claude_settings.uninstall()
        self.assertEqual(self.read(), {"hooks": {"Stop": [{"hooks": [FOREIGN]}]}})

    def test_uninstall_drops_empty_hooks_key(self):
        self.write({"model": "opus"})
        claude_settings.install(COMMAND)
        claude_settings.uninstall()
        self.assertEqual(self.read(), {"model": "opus"})
        self.assertTrue(os.path.exists(claude_settings.settings_path() + ".claudication.bak"))
