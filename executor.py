import os
import functions as f
import signal
import sys
import shlex

cmd = "grep py < test.txt && echo Done"


def run_stage(cmd, redirects, stdin_fd=None, stdout_fd=None,):
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    if stdin_fd != None:
        os.dup2(stdin_fd,0)
        os.close(stdin_fd)
    
    if stdout_fd != None:
        os.dup2(stdout_fd,1)
        os.close(stdout_fd)
    
    for operator, filename in redirects:
        if operator == ">":
            try:
                file_fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
            except OSError as e:
                print(f"Error: {e.strerror}: '{filename}'", file=sys.stderr)
                os._exit(1)
            os.dup2(file_fd, 1)
            os.close(file_fd)
        elif operator == ">>":
            try:
                file_fd = os.open(filename, os.O_WRONLY | os.O_CREAT | os.O_APPEND)
            except OSError as e:
                print(f"Error: {e.strerror}: '{filename}'", file=sys.stderr)
                os._exit(1)
            os.dup2(file_fd, 1)
            os.close(file_fd)
        elif operator == "<":
            try:
                file_fd = os.open(filename, os.O_RDONLY)
            except OSError as e:
                print(f"Error: {e.strerror}: '{filename}'", file=sys.stderr)
                os._exit(1)
            os.dup2(file_fd, 0)
            os.close(file_fd)
    f.run(cmd)

    def run_segment(segment, background=False):
        pipes = [os.pipe() for _ in range(len(segment)-1)]
        pids = []
        for i, stage in enumerate(segment):
            cmd, redirects = stage
            if i > 0:
                stdin_fd = pipes[i-1][0]
            else:
                stdin_fd = None
            
            if i < len(segment) - 1:
                stdout_fd = pipes[i][1]
            else:
                stdout_fd = None
            pid = os.fork()
            pids.append(pid)
            if pid == 0: 
                for j, (r, w) in enumerate(pipes):
                    if j != i - 1:
                        os.close(r)
                    if j != i:
                        os.close(w)
                signal.signal(signal.SIGINT, signal.SIG_DFL)
                os.setpgid(0, 0)
                run_stage(cmd, redirects, stdin_fd, stdout_fd)
        for r, w in pipes:
            os.close(r)
            os.close(w)
        for i, pid in enumerate(pids):
            if background:
                os.setpgid(pid, pid)
                f.background_pids.append(pid)
                f.background_cmds.append(cmd) #Wrong cmd, I need to fix this 
            else:
                if i == len(pids):
                    return os.waitpid(pid, 0)
