import io
import json
from unittest import mock

from claudication import config, hook, state
from tests.support import IsolatedTestCase


class HookTest(IsolatedTestCase):
    def run_hook(self, event, **payload):
        payload = {"hook_event_name": event, "session_id": "s1", "cwd": "/work/project", **payload}
        with mock.patch("sys.stdin", io.StringIO(json.dumps(payload))):
            hook.main()

    def test_events_update_state(self):
        self.run_hook("UserPromptSubmit")
        self.assertEqual(state.summary()["state"], "busy")
        self.run_hook("Stop")
        self.assertEqual(state.summary(), {"state": "ready", "busy": 0, "total": 1})
        self.run_hook("SessionEnd")
        self.assertEqual(state.summary()["total"], 0)

    def test_permission_prompt_means_ready_and_next_tool_means_busy(self):
        self.run_hook("PreToolUse")
        self.run_hook("Notification", notification_type="permission_prompt")
        self.assertEqual(state.summary()["state"], "ready")
        self.run_hook("PreToolUse")
        self.assertEqual(state.summary()["state"], "busy")

    def test_unknown_event_and_bad_input_are_ignored(self):
        self.run_hook("SomethingNew")
        with mock.patch("sys.stdin", io.StringIO("not json")):
            hook.main()
        self.assertEqual(state.summary()["total"], 0)

    @mock.patch("claudication.notify.send")
    def test_no_notifications_unless_enabled(self, send):
        self.run_hook("Stop")
        send.assert_not_called()

    @mock.patch("claudication.notify.send")
    def test_notifications_when_enabled(self, send):
        config.save({"notifications": True})
        self.run_hook("Stop")
        self.run_hook("Notification", notification_type="permission_prompt", message="Claude needs your permission to use Bash")
        titles = [c.args[0] for c in send.call_args_list]
        self.assertEqual(titles, ["Claude is ready · project", "Claude needs you · project"])
        self.assertEqual(send.call_args_list[1].args[1], "Claude needs your permission to use Bash")
        self.assertTrue(send.call_args.kwargs["sound"])

    @mock.patch("claudication.notify.send")
    def test_sound_setting_is_passed_to_notifier(self, send):
        config.save({"notifications": True, "sound": False})
        self.run_hook("Stop")
        self.assertFalse(send.call_args.kwargs["sound"])

    @mock.patch("claudication.notify.send")
    def test_idle_reminder_is_not_notified(self, send):
        config.save({"notifications": True})
        self.run_hook("Notification", notification_type="idle_prompt")
        self.run_hook("Notification", message="Claude is waiting for your input")
        send.assert_not_called()

    @mock.patch("claudication.notify.send", side_effect=OSError("no notifier"))
    def test_notifier_failure_does_not_raise(self, send):
        config.save({"notifications": True})
        self.run_hook("Stop")
        self.assertEqual(state.summary()["state"], "ready")
