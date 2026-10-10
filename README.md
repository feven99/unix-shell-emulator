# Variant 24 — Stage 3 (reconstructed checkpoint)

Stage 1–2 functionality plus an **in-memory XML virtual filesystem**.
Binary file contents use Base64, and all operations stay in memory.
`ls` and `cd` now operate on virtual files and folders, including nested paths.
`who` and `pwd` are added in Stage 4; `cp` and `rmdir` in Stage 5.

Try: `python main.py --vfs data/filesystem.xml --script scripts/test_vfs.sh --no-repl`
Test: `python -m unittest discover -s tests -v`

**History notice:** Retrospectively reconstructed checkpoint.
