#!/usr/bin/env python3
"""Entry point for all five stages of the UNIX shell emulator assignment."""
import argparse
import sys

from shell_emulator import Emulator, VFSError


def main(argv=None):
    parser = argparse.ArgumentParser(description="In-memory UNIX shell emulator")
    parser.add_argument("--vfs", required=True, help="Path to XML virtual filesystem")
    parser.add_argument("--prompt", help="Optional literal REPL prompt")
    parser.add_argument("--log", help="JSON Lines event log file path")
    parser.add_argument("--script", help="Startup script of emulator commands")
    parser.add_argument("--no-repl", action="store_true", help="Run startup script and exit")
    args = parser.parse_args(argv)
    print("Configuration:", vars(args), file=sys.stderr)
    try:
        emulator = Emulator(args.vfs, args.prompt, args.log)
        if args.script:
            emulator.run_script(args.script)
        if not args.no_repl and emulator.running:
            emulator.repl()
    except (OSError, ValueError, VFSError) as exc:
        parser.exit(1, f"shell: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
