#!/usr/bin/env python3
import atexit
import getpass
import os
import readline
import shlex
import socket
import signal
import functions as f
import parser as p
import executor as e

purple = "\001\033[35m\002"
green = "\001\033[32m\002"
blue = "\001\033[34m\002"
default = "\001\033[0m\002"

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
print(f"{purple}╭─ {green}{username}{purple}@{green}{hostname}{purple}:{blue}{os.getcwd()}")
cmd = input(f"{purple}╰─{default}$")


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
        display_cmd = cmd 
        if cmd_split[0] == "time":
            f.mytime(cmd,background,display_cmd)
        elif cmd == "jobs":
            if len(f.background_pids) == 0:
                print("No background jobs running.")
            else:
                print("-------======= Running Jobs ======= -------")
                for i in range(len(f.background_pids)):
                    print(f"[{f.background_pids[i]}]: {f.background_cmds[i]}")
        elif cmd_split[0] == "cd":
            f.cd(cmd_split)
        else:
            cmd, operations = p.parser(cmd)
            if background:
                pid = os.fork()
                if pid == 0:
                    os.setpgid(pid,pid)
                    e.run_parsed(cmd, operations)
                    os._exit(0)
                else:
                    f.background_pids.append(pid)
                    f.background_cmds.append(display_cmd)
            else:
                e.run_parsed(cmd, operations)


    for pid in f.background_pids:
        if os.waitpid(pid, os.WNOHANG) != (0, 0):
            background_finished.append(pid)

    for pid in background_finished:
        index = f.background_pids.index(pid)
        print(f"[{pid}]+ Done {f.background_cmds[index]}")
        f.background_pids.pop(index)
        f.background_cmds.pop(index)

    background_finished=[]
    print(f"{purple}╭─ {green}{username}{purple}@{green}{hostname}{purple}:{blue}{os.getcwd()}")
    cmd = input(f"{purple}╰─{default}$")
