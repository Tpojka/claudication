"""Test isolation: every test gets its own home and data directory."""
import os
import tempfile
import unittest
from unittest import mock


class IsolatedTestCase(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = tmp.name
        self.data = os.path.join(self.home, "data")
        env = {"HOME": self.home, "USERPROFILE": self.home, "CLAUDICATION_HOME": self.data}
        patcher = mock.patch.dict(os.environ, env)
        patcher.start()
        self.addCleanup(patcher.stop)
