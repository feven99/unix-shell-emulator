#!/usr/bin/env python3
"""Stage 2: configurable startup, REPL, logging, and command scripts."""
import argparse
import sys
from shell_emulator import Emulator

def main(argv=None):
    parser = argparse.ArgumentParser(description="UNIX shell emulator (stage 2)")
    parser.add_argument("--vfs", help="XML VFS path (used starting in Stage 3)")
    parser.add_argument("--prompt", help="Custom prompt")
    parser.add_argument("--log", help="JSON Lines log path")
    parser.add_argument("--script", help="Startup script")
    parser.add_argument("--no-repl", action="store_true")
    args = parser.parse_args(argv)
    print("Configuration:", vars(args), file=sys.stderr)
    emulator = Emulator(args.vfs, args.prompt, args.log)
    try:
        if args.script:
            emulator.run_script(args.script)
        if not args.no_repl and emulator.running:
            emulator.repl()
    except OSError as exc:
        parser.exit(1, f"shell: {exc}\n")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
