import io
import unittest
from pathlib import Path
from shell_emulator import Emulator
XML = Path(__file__).resolve().parents[1] / 'data' / 'filesystem.xml'

class StageFourTests(unittest.TestCase):
    def setUp(self):
        self.output = io.StringIO()
        self.shell = Emulator(str(XML), output=self.output)

    def test_ls_cd_pwd_who(self):
        for cmd in ['pwd', 'ls /', 'cd /home/student', 'pwd', 'ls', 'who']:
            self.assertEqual(self.shell.execute(cmd), 0, cmd)
        text = self.output.getvalue()
        self.assertIn('/home/student', text)
        self.assertIn('hello.txt', text)
        self.assertIn(self.shell.hostname, text)

    def test_errors_and_quote_expansion(self):
        self.shell.env['TEST_HOME']='/home/student'
        self.assertEqual(self.shell.execute('cd "$TEST_HOME"'),0)
        self.assertEqual(self.shell.execute('cd /missing'),1)
        self.assertEqual(self.shell.execute('pwd extra'),1)
        self.assertEqual(self.shell.execute('cp /x /y'),1) # introduced in Stage 5

if __name__ == '__main__':
    unittest.main()
