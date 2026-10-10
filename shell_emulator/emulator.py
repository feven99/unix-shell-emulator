"""Stage 2 (reconstructed): configuration, logging and startup scripts."""
from __future__ import annotations
import getpass
import json
import os
import re
import shlex
import socket
import sys
from datetime import datetime, timezone
from typing import TextIO

VARIABLE = re.compile(r'\$([A-Za-z_][A-Za-z0-9_]*)|\$\{([A-Za-z_][A-Za-z0-9_]*)\}')


class Emulator:
    def __init__(self, vfs_path: str | None = None, prompt: str | None = None,
                 log_path: str | None = None, output: TextIO | None = None):
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.output = output or sys.stdout
        self.env = dict(os.environ)
        self.env.setdefault("USER", self.username)
        self.env.setdefault("HOME", os.path.expanduser("~"))
        self.running = True
        self.vfs_path = vfs_path  # Stage 2 accepts a path; loading comes in Stage 3.
        self.prompt_template = prompt
        self.log_path = log_path
        self.last_status = 0

    def prompt(self) -> str:
        return self.prompt_template if self.prompt_template is not None else f"{self.username}@{self.hostname}:~$ "

    def print(self, message: str = "") -> None:
        print(message, file=self.output)

    def _expand(self, text: str) -> str:
        """Shell-style variable expansion outside single quotes, including double quotes."""
        result = []
        i = 0
        quote = None
        while i < len(text):
            ch = text[i]
            if ch == "\\" and quote != "'" and i + 1 < len(text):
                result.append(text[i:i + 2])
                i += 2
                continue
            if ch in ("'", '"'):
                if quote is None:
                    quote = ch
                elif quote == ch:
                    quote = None
                result.append(ch)
                i += 1
                continue
            if ch == "$" and quote != "'":
                match = VARIABLE.match(text, i)
                if match:
                    name = match.group(1) or match.group(2)
                    # Quote the replacement safely for shlex without breaking double quoting.
                    value = self.env.get(name, "")
                    if quote == '"':
                        value = value.replace("\\", "\\\\").replace('"', '\\"')
                    else:
                        value = shlex.quote(value) if value else "''"
                    result.append(value)
                    i = match.end()
                    continue
            result.append(ch)
            i += 1
        return "".join(result)

    def execute(self, line: str) -> int:
        command, args, status = "", [], 0
        try:
            parts = shlex.split(self._expand(line), posix=True)
            if not parts:
                return 0
            command, args = parts[0], parts[1:]
            if command == "exit":
                if args:
                    raise ValueError("exit: expected 0 arguments")
                self.running = False
            elif command in ("ls", "cd"):
                self.print(f"{command}: stub args={args!r}")
            else:
                raise ValueError(f"{command}: command not found")
        except ValueError as exc:
            self.print(f"shell: {exc}")
            status = 1
        finally:
            self.last_status = status
            if command and self.log_path:
                event = {"timestamp": datetime.now(timezone.utc).isoformat(),
                         "command": command, "args": args, "raw": line,
                         "status": status}
                with open(self.log_path, "a", encoding="utf-8") as log:
                    log.write(json.dumps(event) + "\n")
        return status

    def run_script(self, script_path: str) -> None:
        with open(script_path, encoding="utf-8") as source:
            for raw in source:
                line = raw.rstrip("\r\n")
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                self.print(f"{self.prompt()}{line}")
                self.execute(line)
                if not self.running:
                    break

    def repl(self) -> None:
        while self.running:
            try:
                line = input(self.prompt())
            except EOFError:
                self.print()
                break
            except KeyboardInterrupt:
                self.print()
                continue
            self.execute(line)
