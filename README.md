# UNIX-like shell emulator — Variant 24

A Python 3 implementation of all five stages of the assignment, reconstructed as separate retrospective commits. Runs on Windows, macOS or Linux using only the Python standard library.

## Quick start

Requires Python **3.10+**. No packages to install.

```bash
cd unix_shell_emulator
python main.py --vfs data/filesystem.xml
```

The CLI uses the **actual OS username and hostname** in its default prompt, but paths and files for shell commands belong to the **virtual** filesystem, not the host OS. `HOME` and other `$VARIABLE` values come from the real OS environment. The virtual working directory starts at `/`, regardless of the host directory.

Try:

```text
ls /
cd /home/student
pwd
ls
md5 hello.txt
cp hello.txt /tmp/new.txt
ls /tmp
md5 /tmp/new.txt
who
rmdir /tmp
exit
```

### Command-line configuration (Stage 2)

```bash
python main.py --vfs data/filesystem.xml --prompt 'demo$ ' --log shell.jsonl --script scripts/test_config.sh --no-repl
```

| Flag | Meaning |
|---|---|
| `--vfs FILE` | Required XML VFS path |
| `--prompt TEXT` | Literal prompt replacing the default `username@hostname:/path$ ` |
| `--log FILE` | Append one JSON object per command to this JSON Lines file |
| `--script FILE` | Run script commands first (one emulator command per line) |
| `--no-repl` | Exit after script instead of entering interactive mode |

Debug output of parsed CLI configuration is printed to **stderr** on startup.

### Running scripts (Stages 2–5)

Scripts are **plain text** containing emulator commands, not OS shell programs. `#` full-line comments and blank lines are ignored. Each executed command is echoed with a prompt; the same dispatcher is used in interactive and scripted modes. `exit` stops the script and the REPL.

```bash
python main.py --vfs data/filesystem.xml --script scripts/test_config.sh --log config.jsonl --no-repl
python main.py --vfs data/filesystem.xml --script scripts/test_vfs.sh --no-repl
python main.py --vfs data/filesystem.xml --script scripts/test_commands.sh --no-repl
python main.py --vfs data/filesystem.xml --script scripts/test_rmdir.sh --no-repl
```

### Testing

```bash
python -m unittest discover -s tests -v
```

### VFS XML format (Stage 3)

```xml
<vfs>
  <dir name="home">
    <file name="hello.txt" encoding="base64">SGVsbG8K</file>
  </dir>
</vfs>
```

`<dir>` can be nested to any depth; `<file>` text stores **Base64-encoded bytes**. File loading, directory navigation, listing, copying and hashing take place completely in Python memory. XML is never written back, and host files are never modified by virtual commands.

### Supported emulator commands (Stages 1, 4, 5)

| Command | Behavior |
|---|---|
| `ls [path]` | Show alphabetically sorted entries, or a file name |
| `cd [path]` | Set virtual working directory (defaults to `/`) |
| `pwd` | Print virtual working directory |
| `who` | Print current OS username and hostname (simplified model of `who`) |
| `cp SOURCE DEST` | Copy/overwrite one regular virtual file, optionally to an existing directory |
| `md5 FILE` | Show MD5 digest of virtual file contents (extra feature) |
| `rmdir DIR` | Remove an empty VFS directory (in memory only) |
| `exit` | Close emulator |

Invalid arity, unknown commands, invalid VFS paths, malformed quoting, trying to `cd` into a file, trying to copy a directory, and trying to hash a directory result in error messages and nonzero command status. `$NAME` and `${NAME}` environment variables expand unless enclosed in single quotes; escaping and double-quoted expansion are supported for typical inputs. This is an educational emulator rather than a full POSIX shell: it does not implement pipelines, redirection, glob expansion, semicolons, or full shell expansion semantics.

### Retrospectively reconstructed stage commits

This branch contains five runnable reconstructed code checkpoints, one for each
assignment stage: REPL, configuration, VFS, base commands, and extra commands.
Each checkpoint was created **after** the full project existed, so this is **not**
the original chronological development history. The student's original
`main` branch and its two genuine commits are preserved separately.

Run `python -m unittest discover -s tests -v` for each checkpoint.

### Architecture

- `main.py`: argument parsing, setup and REPL entry point.
- `shell_emulator/emulator.py`: command parsing and execution, state, logging, scripts.
- `shell_emulator/vfs.py`: in-memory VFS loaded once from XML.
- `data/filesystem.xml`: example with three levels of directories.
- `scripts/`: separate stage test scripts.
- `tests/`: automated `unittest` checks and edge cases.
