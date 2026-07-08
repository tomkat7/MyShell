#!/usr/bin/env python3
import atexit
import getpass
import os
import readline
import shlex
import socket
import signal
import functions as f

background_finished=[]
signal.signal(signal.SIGINT, signal.SIG_IGN)

histfile = os.path.expanduser("~/.mysh_history")
try:
    readline.read_history_file(histfile)
except FileNotFoundError:
    pass
atexit.register(readline.write_history_file, histfile)


username = getpass.getuser()
hostname = socket.gethostname()
cmd = input(f"{username}@{hostname}:{os.getcwd()}$")
while cmd != "exit":
    if cmd == "":
        print()
    else:
        cmd_split = shlex.split(cmd)
        if cmd_split[-1] == "&":
            cmd_split.pop(-1)
            cmd=cmd.removesuffix("&")
            background=True
        else:
            background=False
        if cmd_split[0] == "time":
            f.mytime(cmd_split)
        elif cmd == "jobs":
            if len(f.background_pids) == 0:
                print("No background jobs running.")
            else:
                print("-------======= Running Jobs ======= -------")
                for i in range(len(f.background_pids)):
                    print(f"[{f.background_pids[i]}]: {f.background_cmds[i]}")
        elif "||" in cmd_split or "&&" in cmd_split:
            f.chain(cmd)
        elif "<" in cmd_split:
            f.input_redirection(cmd,background)
        elif "|" in cmd_split:
            f.pipe(cmd,background)
        elif ">" in cmd_split:
            f.redirect(cmd,background)
        else:
            if cmd_split[0] == "cd":
                f.cd(cmd_split)
            else:
                f.execute(cmd_split,background)
    for pid in f.background_pids:
        if os.waitpid(pid, os.WNOHANG) != (0, 0):
            background_finished.append(pid)
    for pid in background_finished:
        index = f.background_pids.index(pid)
        print(f"[{pid}]+ Done {f.background_cmds[index]}")
        f.background_pids.pop(index)
        f.background_cmds.pop(index)
    background_finished=[]
    cmd = input(f"{username}@{hostname}:{os.getcwd()}$")
