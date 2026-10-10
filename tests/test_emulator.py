import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from shell_emulator import Emulator, VirtualFS, VFSError

ROOT = Path(__file__).resolve().parents[1]
XML = ROOT / "data" / "filesystem.xml"


class EmulatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.output = io.StringIO()
        self.log = Path(self.tmp.name) / "events.jsonl"
        self.shell = Emulator(str(XML), log_path=str(self.log), output=self.output)

    def test_initial_root_and_navigation(self):
        self.assertEqual(self.shell.cwd, "/")
        self.assertEqual(self.shell.execute("pwd"), 0)
        self.assertEqual(self.shell.execute("ls /"), 0)
        self.assertIn("home", self.output.getvalue())
        self.assertEqual(self.shell.execute("cd /home/student/documents"), 0)
        self.assertEqual(self.shell.cwd, "/home/student/documents")
        self.assertEqual(self.shell.execute("cd .."), 0)
        self.assertEqual(self.shell.cwd, "/home/student")
        self.assertEqual(self.shell.execute("cd"), 0)
        self.assertEqual(self.shell.cwd, "/")

    def test_expansion_and_quote_handling(self):
        self.shell.env["MYDIR"] = "/home/student"
        self.assertEqual(self.shell.execute("cd $MYDIR"), 0)
        self.assertEqual(self.shell.execute('ls "$MYDIR"'), 0)
        self.assertEqual(self.shell.execute("cd '$MYDIR'"), 1)
        self.assertEqual(self.shell.cwd, "/home/student")
        self.assertEqual(self.shell.execute('ls "unterminated'), 1)

    def test_invalid_commands_and_arity(self):
        self.assertEqual(self.shell.execute("nocommand"), 1)
        self.assertEqual(self.shell.execute("pwd extra"), 1)
        self.assertEqual(self.shell.execute("cd /absent"), 1)
        self.assertEqual(self.shell.execute("cd /home/student/hello.txt"), 1)
        self.assertEqual(self.shell.execute("ls /home/student/hello.txt"), 0)
        self.assertIn("command not found", self.output.getvalue())

    def test_copy_and_md5_in_memory(self):
        before = XML.read_bytes()
        self.assertEqual(self.shell.execute("cp /home/student/hello.txt /tmp"), 0)
        self.assertEqual(self.shell.execute("md5 /tmp/hello.txt"), 0)
        expected = hashlib.md5(b"Hello from the virtual file system!\n").hexdigest()
        self.assertIn(expected, self.output.getvalue())
        self.assertEqual(self.shell.execute("cp /tmp/hello.txt /tmp/new.txt"), 0)
        self.assertEqual(self.shell.vfs.get("/tmp/new.txt").content,
                         self.shell.vfs.get("/tmp/hello.txt").content)
        self.assertEqual(before, XML.read_bytes())
        new_shell = Emulator(str(XML), output=io.StringIO())
        with self.assertRaises(VFSError):
            new_shell.vfs.get("/tmp/hello.txt")

    def test_cp_failure_modes(self):
        for args in ["cp /tmp /home", "cp /missing /tmp/x", "cp /home/student/hello.txt /missing/x", "cp /home/student/hello.txt /home/student/hello.txt", "cp /home/student/hello.txt /etc/os-release"]:
            # Overwriting a different existing file is valid.
            expected = 0 if args.endswith("/etc/os-release") else 1
            self.assertEqual(self.shell.execute(args), expected, args)
        self.assertEqual(self.shell.execute("md5 /home"), 1)

    def test_logger(self):
        self.shell.execute("pwd")
        self.shell.execute("not-found")
        events = [json.loads(x) for x in self.log.read_text().splitlines()]
        self.assertEqual([e["status"] for e in events], [0, 1])
        self.assertEqual(events[0]["command"], "pwd")
        self.assertIn("timestamp", events[0])

    def test_script_and_exit(self):
        script = Path(self.tmp.name) / "test.sh"
        script.write_text("# ignored\npwd\nwho\nexit\npwd\n", encoding="utf-8")
        self.shell.run_script(str(script))
        self.assertFalse(self.shell.running)
        events = [json.loads(x) for x in self.log.read_text().splitlines()]
        self.assertEqual([x["command"] for x in events], ["pwd", "who", "exit"])

    def test_invalid_xml(self):
        file = Path(self.tmp.name) / "invalid.xml"
        file.write_text('<vfs><dir name="x"/><dir name="x"/></vfs>')
        with self.assertRaises(VFSError):
            VirtualFS(str(file))
        file.write_text('<vfs><file name="a">$$$$</file></vfs>')
        with self.assertRaises(VFSError):
            VirtualFS(str(file))


if __name__ == "__main__":
    unittest.main()
