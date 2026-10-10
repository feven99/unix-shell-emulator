"""Stage 1 (reconstructed): interactive shell with stub commands."""
from __future__ import annotations
import getpass
import os
import re
import shlex
import socket
import sys
from typing import TextIO

VARIABLE = re.compile(r'\$([A-Za-z_][A-Za-z0-9_]*)|\$\{([A-Za-z_][A-Za-z0-9_]*)\}')


class Emulator:
    def __init__(self, output: TextIO | None = None):
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.output = output or sys.stdout
        self.env = dict(os.environ)
        self.env.setdefault("USER", self.username)
        self.env.setdefault("HOME", os.path.expanduser("~"))
        self.running = True

    def prompt(self) -> str:
        return f"{self.username}@{self.hostname}:~$ "

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
        try:
            parts = shlex.split(self._expand(line), posix=True)
        except ValueError as exc:
            self.print(f"shell: {exc}")
            return 1
        if not parts:
            return 0
        command, args = parts[0], parts[1:]
        if command == "exit":
            if args:
                self.print("shell: exit: expected 0 arguments")
                return 1
            self.running = False
        elif command in ("ls", "cd"):
            # Stage 1: stubs show the parsed arguments; there is no VFS yet.
            self.print(f"{command}: stub args={args!r}")
        else:
            self.print(f"shell: {command}: command not found")
            return 1
        return 0

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
