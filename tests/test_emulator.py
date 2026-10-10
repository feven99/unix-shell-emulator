import io
import json
import tempfile
import unittest
from pathlib import Path
from shell_emulator import Emulator

class StageTwoTests(unittest.TestCase):
    def test_script_logging_prompt_and_errors(self):
        with tempfile.TemporaryDirectory() as temporary:
            file = Path(temporary) / "test.sh"
            log = Path(temporary) / "events.jsonl"
            file.write_text('# comment\nls $HOME\ncd /tmp\nunknown\nexit\nls /\n', encoding='utf-8')
            output = io.StringIO()
            shell = Emulator(prompt='demo$ ', log_path=str(log), output=output)
            shell.run_script(str(file))
            self.assertFalse(shell.running)
            self.assertIn('demo$ ', output.getvalue())
            events = [json.loads(x) for x in log.read_text().splitlines()]
            self.assertEqual([x['command'] for x in events], ['ls','cd','unknown','exit'])
            self.assertEqual([x['status'] for x in events], [0,0,1,0])
            self.assertIn('timestamp', events[0])

if __name__ == '__main__':
    unittest.main()
