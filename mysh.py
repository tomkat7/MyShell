#!/usr/bin/env python3
import atexit
import getpass
import os
import readline
import shlex
import socket
import sys
import time

histfile = os.path.expanduser("~/Projects/Python/Shell/.mysh_history")
try:
    readline.read_history_file(histfile)
except FileNotFoundError:
    pass
atexit.register(readline.write_history_file, histfile)


def run(cmd):
    try:
        os.execvp(cmd[0], cmd)
    except FileNotFoundError:
        print(f'Error: Command "{cmd[0]}" was not found.', file=sys.stderr)
        os._exit(1)
    except PermissionError:
        print(f'Error: Permission denied: "{cmd[0]}"', file=sys.stderr)
        os._exit(1)


def pipe(cmd):
    parts = [shlex.split(p.strip()) for p in cmd.split("|")]
    n = len(parts)
    pipes = [os.pipe() for x in range(n - 1)]

    pids = []
    for i in range(n):
        pid = os.fork()
        if pid == 0:
            if i > 0:
                os.dup2(pipes[i - 1][0], 0)
            if i < n - 1:
                os.dup2(pipes[i][1], 1)
            for j, (r, w) in enumerate(pipes):
                if j != i - 1:
                    os.close(r)
                if j != i:
                    os.close(w)
            if i == n - 1 and ">" in cmd.split("|")[-1]:
                if cmd.split("|")[-1].count(">") == 1:
                    segment = cmd.split("|")[-1]
                    command_part, filename = segment.split(">", 1)
                    filename = filename.strip()
                    command_part = shlex.split(command_part.strip())
                    file_fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
                    os.dup2(file_fd, 1)
                    os.close(file_fd)
                    run(command_part)
                elif cmd.split("|")[-1].count(">") == 2:
                    segment = cmd.split("|")[-1]
                    command_part, filename = segment.split(">", 1)
                    filename = filename.strip()
                    command_part = shlex.split(command_part.strip())
                    file_fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
                    os.dup2(file_fd, 1)
                    os.close(file_fd)
                    run(command_part)
            else:
                run(parts[i])
        pids.append(pid)

    for r, w in pipes:
        os.close(r)
        os.close(w)
    for pid in pids:
        os.waitpid(pid, 0)


def cd(cmd):
    if len(cmd) == 2:
        try:
            os.chdir(os.path.expanduser(cmd[1]))
        except FileNotFoundError:
            print(f'Error: The directory "{cmd[1]}" does not exist.')
    else:
        os.chdir(os.path.expanduser("~"))


def execute(cmd):
    pid = os.fork()
    if pid == 0:
        run(cmd)
    else:
        return os.waitpid(pid, 0)


def redirect(cmd):
    count = cmd.count(">")
    cmd = cmd.split(">")
    filename = cmd[1].strip()
    command = cmd[0].strip()
    file_fd = None
    if count == 1:
        file_fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
        pid = os.fork()
        if pid == 0:
            os.dup2(file_fd, 1)
            os.close(file_fd)
            command = shlex.split(command)
            run(command)
    elif count == 2:
        file_fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
        pid = os.fork()
        if pid == 0:
            os.dup2(file_fd, 1)
            os.close(file_fd)
            command = shlex.split(command)
            run(command)
    else:
        print("Error: Redirection not possible.")
        return
    if file_fd != None:
        os.close(file_fd)
    os.waitpid(pid, 0)


def mytime(cmd):
    rest = cmd[1:]
    start = time.perf_counter()
    if "|" in " ".join(rest):
        pipe(" ".join(rest))
    elif ">" in " ".join(rest):
        redirect(" ".join(rest))
    else:
        execute(rest)
    end = time.perf_counter()
    print(f"Elapsed time = {end - start:.3f}")


def double_command(cmd, operation):
    if operation == 0:
        cmd = cmd.split("||")
        part1 = cmd[0].strip()
        part2 = cmd[1].strip()
        status = execute(shlex.split(part1))
        if os.WIFEXITED(status[1]):
            exit_code = os.WEXITSTATUS(status[1])
            if exit_code != 0:
                execute(shlex.split(part2))
    elif operation == 1:
        cmd = cmd.split("&&")
        part1 = cmd[0].strip()
        part2 = cmd[1].strip()
        status = execute(shlex.split(part1))
        if os.WIFEXITED(status[1]):
            exit_code = os.WEXITSTATUS(status[1])
            if exit_code == 0:
                execute(shlex.split(part2))


username = getpass.getuser()
hostname = socket.gethostname()
cmd = input(f"{username}@{hostname}:{os.getcwd()}$")
while cmd != "exit":
    if cmd == "":
        print()
    else:
        cmd_split = shlex.split(cmd)
        if cmd_split[0] == "time":
            mytime(cmd_split)
        elif "||" in cmd_split:
            double_command(cmd, 0)
        elif "&&" in cmd_split:
            double_command(cmd, 1)
        elif "|" in cmd:
            pipe(cmd)
        elif ">" in cmd:
            redirect(cmd)
        elif "aigeas" in cmd:
            cmd = 'echo "Ορφέας Πιταούλης"'
            execute(shlex.split(cmd))
        else:
            if cmd_split[0] == "cd":
                cd(cmd_split)
            else:
                execute(cmd_split)
    cmd = input(f"{username}@{hostname}:{os.getcwd()}$")
