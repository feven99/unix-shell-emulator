"""Stage 3: virtual shell, logging and script execution."""
from __future__ import annotations

import getpass
import json
import os
import posixpath
import re
import shlex
import socket
import sys
from datetime import datetime, timezone
from typing import TextIO

from .vfs import VirtualFS, VFSError

VARIABLE = re.compile(r'\$([A-Za-z_][A-Za-z0-9_]*)|\$\{([A-Za-z_][A-Za-z0-9_]*)\}')


class Emulator:
    def __init__(self, vfs_path: str, prompt: str | None = None,
                 log_path: str | None = None, output: TextIO | None = None):
        self.vfs = VirtualFS(vfs_path)
        self.cwd = "/"
        self.username = getpass.getuser()
        self.hostname = socket.gethostname()
        self.prompt_template = prompt
        self.log_path = log_path
        self.output = output or sys.stdout
        self.running = True
        self.last_status = 0
        self.env = dict(os.environ)
        self.env.setdefault("USER", self.username)
        self.env.setdefault("HOME", os.path.expanduser("~"))
        self.env["PWD"] = self.cwd

    def prompt(self) -> str:
        if self.prompt_template is not None:
            return self.prompt_template
        return f"{self.username}@{self.hostname}:{self.cwd}$ "

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
        """Run one command. Returns 0 for success and nonzero for errors."""
        cmd = ""
        args: list[str] = []
        status = 0
        try:
            parts = shlex.split(self._expand(line), posix=True)
            if not parts:
                return 0
            cmd, args = parts[0], parts[1:]
            commands = {
                "ls": self.cmd_ls, "cd": self.cmd_cd,
                "exit": self.cmd_exit,
            }
            if cmd not in commands:
                raise VFSError(f"{cmd}: command not found")
            commands[cmd](args)
        except (ValueError, VFSError) as exc:
            self.print(f"shell: {exc}")
            status = 1
        finally:
            self.last_status = status
            if cmd:
                self._log(cmd, args, line, status)
        return status

    def _log(self, command: str, args: list[str], raw: str, status: int) -> None:
        if not self.log_path:
            return
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": command, "args": args, "raw": raw,
            "cwd": self.cwd, "status": status,
        }
        with open(self.log_path, "a", encoding="utf-8") as file:
            file.write(json.dumps(event, ensure_ascii=False) + "\n")

    @staticmethod
    def _arity(command: str, args: list[str], minimum: int, maximum: int) -> None:
        if not minimum <= len(args) <= maximum:
            raise VFSError(f"{command}: expected {minimum}" +
                            (f" to {maximum}" if minimum != maximum else "") +
                            f" argument(s), got {len(args)}")

    def cmd_ls(self, args: list[str]) -> None:
        self._arity("ls", args, 0, 1)
        path = args[0] if args else "."
        node = self.vfs.get(path, self.cwd)
        if node.is_dir:
            self.print("  ".join(self.vfs.listdir(path, self.cwd)))
        else:
            self.print(posixpath.basename(self.vfs.normalize(path, self.cwd)))

    def cmd_cd(self, args: list[str]) -> None:
        self._arity("cd", args, 0, 1)
        path = args[0] if args else "/"
        node = self.vfs.get(path, self.cwd)
        if not node.is_dir:
            raise VFSError(f"cd: {path}: not a directory")
        self.cwd = self.vfs.normalize(path, self.cwd)
        self.env["PWD"] = self.cwd

    def cmd_exit(self, args: list[str]) -> None:
        self._arity("exit", args, 0, 0)
        self.running = False

    def run_script(self, script_path: str) -> None:
        with open(script_path, encoding="utf-8") as source:
            for line_no, raw in enumerate(source, 1):
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
