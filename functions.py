import os
import sys
import shlex
import signal
import time
import re


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
            signal.signal(signal.SIGINT, signal.SIG_DFL)
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
        return os.waitpid(pid, 0)


def cd(cmd):
    if len(cmd) == 2:
        try:
            os.chdir(os.path.expanduser(cmd[1]))
            return ("fake error", 0)
        except FileNotFoundError:
            print(f'Error: The directory "{cmd[1]}" does not exist.')
            return ("fake error", 256)
    else:
        os.chdir(os.path.expanduser("~"))
        return ("fake error", 0)


def execute(cmd):
    pid = os.fork()
    if pid == 0:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        run(cmd)
    else:
        return os.waitpid(pid, 0)


def redirect(cmd):
    if " > " in cmd:
        count = 1
        cmd = cmd.split(" > ")
    elif " >> " in cmd:
        count = 2
        cmd = cmd.split(" >> ")
    else: 
        count = -1
    filename = cmd[1].strip()
    command = cmd[0].strip()
    file_fd = None
    if count == 1:
        try:
            file_fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
        except OSError as e:
            print(f"Error: {e.strerror}: '{filename}'", file=sys.stderr)
            return
        pid = os.fork()
        if pid == 0:
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            os.dup2(file_fd, 1)
            os.close(file_fd)
            command = shlex.split(command)
            run(command)
    elif count == 2:
        try:
            file_fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
        except OSError as e:
            print(f"Error: {e.strerror}: '{filename}'", file=sys.stderr)
            return
        pid = os.fork()
        if pid == 0:
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            os.dup2(file_fd, 1)
            os.close(file_fd)
            command = shlex.split(command)
            run(command)
    else:
        print("Error: Redirection not possible.")
        return
    if file_fd != None:
        os.close(file_fd)
    return os.waitpid(pid, 0)

def input_redirection(cmd):
    cmd = cmd.split(" < ")
    filename = cmd[1].strip()
    command = cmd[0]
    file_fd = None
    try:
        file_fd = os.open(filename, os.O_RDONLY)
    except OSError as e:
        print(f"Error: {e.strerror}: '{filename}'", file=sys.stderr)
        return
    pid = os.fork()
    if pid == 0:
            signal.signal(signal.SIGINT, signal.SIG_DFL)
            os.dup2(file_fd, 0)
            os.close(file_fd)
            command = shlex.split(command)
            run(command)

    if file_fd != None:
        os.close(file_fd)    
    return os.waitpid(pid, 0)
    
def mytime(cmd):
    rest = cmd[1:]
    start = time.perf_counter()
    if "|" in " ".join(rest):
        pipe(" ".join(rest))
    elif ">" in " ".join(rest):
        redirect(" ".join(rest))
    elif "||" in " ".join(rest) or "&&" in " ".join(rest):
        double_command(" ".join(rest))
    else:
        execute(rest)
    end = time.perf_counter()
    print(f"Elapsed time = {end - start:.3f}")
    return ("success", 0)


def double_command(cmd):
    operations = []
    cmd_split = shlex.split(cmd)
    for i in cmd_split:
        if i == "||":
            operations.append("||")
        elif i == "&&":
            operations.append("&&")
    cmd_split = re.split(r"\|\||&&", cmd)
    cmd_split = [item.strip() for item in cmd_split if item.strip()]
    parts = [part for part in cmd_split]
    for i in range(len(operations) + 1):
        if shlex.split(parts[i])[0] == "cd":
            status = cd(shlex.split(parts[i]))
        elif shlex.split(parts[i])[0] == "time":
            status = mytime(shlex.split(parts[i]))
        elif "|" in shlex.split(parts[i]):
            status = pipe(parts[i])
        elif ">" in shlex.split(parts[i]):
            status = redirect(parts[i])
        elif "<" in shlex.split(parts[i]):
            status = input_redirection(parts[i])
        else:
            status = execute(shlex.split(parts[i]))
        if os.WIFEXITED(status[1]):
            exit_code = os.WEXITSTATUS(status[1])
            if i > len(operations) - 1:
                i = i - 1
            if operations[i] == "||":
                if exit_code != 0:
                    continue
                else:
                    break
            elif operations[i] == "&&":
                if exit_code == 0:
                    continue
                else:
                    break