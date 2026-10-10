import io
import unittest
import tempfile
from pathlib import Path
from shell_emulator import Emulator, VirtualFS, VFSError
XML = Path(__file__).resolve().parents[1] / 'data' / 'filesystem.xml'

class StageThreeTests(unittest.TestCase):
    def test_vfs_ls_cd_nesting_and_errors(self):
        output = io.StringIO()
        shell = Emulator(str(XML), output=output)
        self.assertEqual(shell.execute('ls /'), 0)
        self.assertIn('home', output.getvalue())
        self.assertEqual(shell.execute('cd /home/student/documents'), 0)
        self.assertEqual(shell.cwd, '/home/student/documents')
        self.assertEqual(shell.execute('ls'), 0)
        self.assertIn('notes.txt', output.getvalue())
        self.assertEqual(shell.execute('cd /home/student/hello.txt'), 1)
        self.assertEqual(shell.execute('cd /not-exist'), 1)
        self.assertEqual(shell.execute('pwd'), 1)  # introduced in Stage 4

    def test_reject_invalid_xml(self):
        with tempfile.TemporaryDirectory() as temp:
            file=Path(temp)/'invalid.xml'
            file.write_text('<vfs><dir name="a"/><dir name="a"/></vfs>')
            with self.assertRaises(VFSError):
                VirtualFS(str(file))
            file.write_text('<vfs><file name="bad">$$$</file></vfs>')
            with self.assertRaises(VFSError):
                VirtualFS(str(file))

if __name__ == '__main__':
    unittest.main()
