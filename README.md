# Variant 24 — Stage 4 (reconstructed checkpoint)

All previous stages plus working UNIX-like `ls`, `cd`, `who` and `pwd`.
`ls` and `cd` operate on the virtual VFS; `who` uses the real OS identity.
Includes script examples of command arguments, paths and error handling.

Try: `python main.py --vfs data/filesystem.xml --script scripts/test_commands.sh --no-repl`
Test: `python -m unittest discover -s tests -v`

**History notice:** Retrospectively reconstructed checkpoint.
