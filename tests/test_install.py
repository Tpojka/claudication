import io
import json
import os
import subprocess
import sys
from contextlib import redirect_stdout

from claudication import config, install, paths
from claudication.install import claude_settings, system
from tests.support import IsolatedTestCase
from tests.test_host import read_message


class InstallTest(IsolatedTestCase):
    def run_installer(self, *args):
        with redirect_stdout(io.StringIO()) as out:
            install.main(list(args))
        return out.getvalue()

    def hook_commands(self):
        with open(claude_settings.settings_path()) as f:
            hooks = json.load(f)["hooks"]
        return {h["command"] for groups in hooks.values() for g in groups for h in g["hooks"]}

    def test_exit_installs_nothing(self):
        self.assertIn("Nothing installed", self.run_installer("3"))
        self.assertFalse(os.path.exists(self.data))

    def test_install_is_self_contained_and_works(self):
        self.addCleanup(system.unregister_host)
        self.run_installer("2")

        self.assertTrue(paths.app_file().is_file())
        self.assertTrue((paths.extension_dir() / "manifest.json").is_file())
        self.assertTrue(paths.icon("knee-ok").is_file())
        self.assertTrue(config.load()["notifications"])
        self.assertEqual(len(self.hook_commands()), 1)

        # The installed app runs on its own: a hook event is recorded as session state.
        payload = json.dumps({"hook_event_name": "UserPromptSubmit", "session_id": "s1"})
        subprocess.run([sys.executable, str(paths.app_file()), "hook"], input=payload.encode(), check=True, cwd=self.home)
        self.assertEqual((paths.sessions_dir() / "s1").read_text(), "busy")

    def test_option_1_turns_notifier_off(self):
        self.addCleanup(system.unregister_host)
        self.run_installer("2")
        self.run_installer("1")
        self.assertFalse(config.load()["notifications"])

    def test_uninstall_removes_everything(self):
        legacy = os.path.join(self.home, ".claude", "claudication", "sessions")
        os.makedirs(legacy)
        self.run_installer("1")
        self.run_installer("uninstall")
        self.assertFalse(os.path.exists(self.data))
        with open(claude_settings.settings_path()) as f:
            self.assertEqual(json.load(f), {})
        self.assertFalse(os.path.exists(legacy))

    def test_chrome_can_start_the_registered_host(self):
        self.addCleanup(system.unregister_host)
        self.run_installer("1")
        manifest = json.loads(system.manifest_path().read_text())
        self.assertEqual(manifest["allowed_origins"], ["chrome-extension://hpoodlefheijkfkpebmooehgnjkibdnc/"])

        # Chrome runs the manifest's path with the extension origin as the argument.
        proc = subprocess.Popen([manifest["path"], "chrome-extension://test/"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        try:
            self.assertEqual(read_message(proc.stdout)["state"], "ready")
            proc.stdin.close()
            self.assertEqual(proc.wait(timeout=10), 0)
        finally:
            proc.kill()
            proc.stdout.close()
