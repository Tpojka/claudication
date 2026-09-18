from pathlib import Path
from unittest import mock

from claudication import notify
from tests.support import IsolatedTestCase

ICON = Path("/data/extension/icons/knee-ok-128.png").resolve()


@mock.patch("claudication.notify.subprocess.Popen")
class NotifyCommandTest(IsolatedTestCase):
    def test_macos_sound_is_optional(self, popen):
        notify._macos("Claude is ready", "Task finished", sound=True)
        notify._macos("Claude is ready", "Task finished", sound=False)
        loud, quiet = (" ".join(c.args[0]) for c in popen.call_args_list)
        self.assertIn('sound name "Glass"', loud)
        self.assertNotIn("sound name", quiet)

    @mock.patch("claudication.notify.shutil.which", return_value="/usr/bin/paplay")
    def test_linux_sound_is_optional(self, which, popen):
        notify._linux("Claude is ready", "Task finished", ICON, sound=True)
        self.assertEqual([c.args[0][0] for c in popen.call_args_list], ["notify-send", "paplay"])
        popen.reset_mock()
        notify._linux("Claude is ready", "Task finished", ICON, sound=False)
        (command,) = [c.args[0] for c in popen.call_args_list]
        self.assertIn("--hint=boolean:suppress-sound:true", command)

    def test_windows_sound_is_optional(self, popen):
        notify._windows("Claude is ready", "Task finished", ICON, sound=True)
        notify._windows("Claude is ready", "Task finished", ICON, sound=False)
        audio = [c.kwargs["env"]["CLAUDICATION_AUDIO"] for c in popen.call_args_list]
        self.assertEqual(audio, [notify.WINDOWS_SOUND, notify.WINDOWS_SILENT])
