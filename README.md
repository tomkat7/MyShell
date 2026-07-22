# MyShell

A Unix shell built from scratch in Python — using raw `fork`, `exec`, and `dup2` syscalls directly, with **no `subprocess` module**. The goal was to actually understand how a shell works under the hood: process creation, file descriptor inheritance, pipes, signal handling, and job control — not just call a library that does it for you.

## Installation

```bash
git clone https://github.com/tomkat7/MyShell.git (or download MyShell.zip from releases)
cd MyShell
chmod +x mysh.py
./mysh.py
```

Requires Python 3 and a Linux (or other POSIX-compliant) system — this shell relies on `os.fork()`, `os.execvp()`, and Unix signal handling, which are not available on Windows.

To exit the shell, type `exit`.

## Features & Syntax

### Running commands
```
ls -la
```
Standard command execution via `fork` + `execvp`.

### Built-ins
```
cd [directory]      # bare `cd` goes to home directory, supports ~ expansion
jobs                 # list currently running background jobs
```

### Piping
```
ls | grep .py
cmd1 | cmd2 | cmd3   # any number of commands
```

### Redirection
```
ls > out.txt         # truncate/overwrite
ls >> out.txt        # append
sort < names.txt     # input redirection
```

### Command chaining
```
cmd1 && cmd2          # run cmd2 only if cmd1 succeeds
cmd1 || cmd2          # run cmd2 only if cmd1 fails
cmd1 && cmd2 && cmd3  # chains of arbitrary length are supported
```

### Timing
```
time ls
time ls | grep .py    # times the whole pipeline/chain, not just the first command
```

### Background jobs
```
sleep 30 &
```
Runs the command without blocking the shell. Background jobs run in their own process group, so they are not killed by Ctrl+C at the prompt. Completion is reported the next time the prompt refreshes:
```
[12345]+ Done sleep 30
```

### Ctrl+C
Cancels the currently running foreground command without killing the shell itself.

## Known Limitations

These are documented, intentional gaps — not oversights:

- **Quoted operators inside pipes**: `grep "a|b"` may not parse correctly, since pipe segments are split on `|` before full tokenization. A proper fix requires a character-by-character tokenizer.
- **Redirection must come after pipes**: in a piped command, `>`/`>>` must be the final operation (e.g. `cmd1 | cmd2 > out.txt` works; other orderings are untested/unsupported).
- **No wildcard/glob expansion**: `ls *.txt` will not expand `*.txt` — the literal string is passed to the command. Deliberately left unimplemented rather than shipping a version that mishandles filenames with spaces.
- **Background jobs cannot be combined with `&&`/`||`, `time`, or `cd`**: `&` is only supported as the terminator of a single, non-chained command.
- **No environment variable support**: no `export`, no `$VAR` expansion.
- **No `fg`/`bg`**: background jobs can be listed with `jobs` but not brought back to the foreground once started.

## Project Structure

- `mysh.py` — main loop, prompt, input dispatch
- `functions.py` — core shell logic (command execution, pipes, redirection, chaining, background jobs)

## Why no `subprocess`?

Using `subprocess` would have solved everything in a few lines, but that defeats the point. This project is about understanding `fork`, `exec`, file descriptor inheritance, and signal handling at the syscall level, not wrapping them.