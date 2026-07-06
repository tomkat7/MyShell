#!/usr/bin/env python3
import atexit
import getpass
import os
import readline
import shlex
import socket
import signal
import functions as f

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
        if cmd_split[0] == "time":
            f.mytime(cmd_split)
        elif "||" in cmd_split or "&&" in cmd_split:
            f.double_command(cmd)
        elif "|" in cmd_split:
            f.pipe(cmd)
        elif ">" in cmd_split:
            f.redirect(cmd)
        elif "<" in cmd_split:
            f.input_redirection(cmd)
        else:
            if cmd_split[0] == "cd":
                f.cd(cmd_split)
            else:
                f.execute(cmd_split)
    cmd = input(f"{username}@{hostname}:{os.getcwd()}$")
