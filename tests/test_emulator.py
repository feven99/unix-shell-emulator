import io
import unittest
from unittest.mock import patch
from shell_emulator import Emulator

class StageOneTests(unittest.TestCase):
    def setUp(self):
        self.output = io.StringIO()
        self.shell = Emulator(output=self.output)

    def test_prompt_uses_real_host_and_user(self):
        self.assertIn(self.shell.username, self.shell.prompt())
        self.assertIn(self.shell.hostname, self.shell.prompt())

    def test_stub_commands_and_expansion(self):
        self.shell.env['TEST_PATH'] = 'two words'
        self.assertEqual(self.shell.execute('ls "$TEST_PATH"'), 0)
        self.assertIn("two words", self.output.getvalue())
        self.assertEqual(self.shell.execute('cd /tmp'), 0)

    def test_exit_errors_and_interactive_mode(self):
        self.assertEqual(self.shell.execute('unknown'), 1)
        self.assertEqual(self.shell.execute('exit extra'), 1)
        with patch('builtins.input', side_effect=['ls /', 'exit']):
            self.shell.repl()
        self.assertFalse(self.shell.running)

if __name__ == '__main__':
    unittest.main()
