# Variant 24 — Stage 2 (reconstructed checkpoint)

Stage 1 plus configurable options `--vfs`, `--prompt`, `--log`, `--script`,
`--no-repl`. Startup configuration is printed; commands are logged as JSON
Lines with timestamps and input/output echo. `ls` and `cd` are still stubs.

Try: `python main.py --prompt "demo$ " --log commands.jsonl --script scripts/test_config.sh --no-repl`
Test: `python -m unittest discover -s tests -v`

**History notice:** Retrospectively reconstructed checkpoint, not original
chronological development history.
