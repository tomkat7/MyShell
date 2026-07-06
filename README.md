This is a very simple linux shell built in python. 
My goal is to learn how shells work, and the best way to do it is building one from scratch. 
I don't use the subprocess python library because then I wouldn't learn about proceses, forks etc.

Use Instructions

**Installation:**
1) Download the `mysh.py` file
2) Make it executable with `chmod +x mysh.py`
3) Run it with `./mysh.py`

**Things to know:**
- To exit, type `exit` and hit enter.
- ctrl+c to stop commands doesn't work yet, so doing ctrl+c will stop the shell instead of the command.
- When using pipes and redirections in the same command, the redirection has to be the last operation. 
- Pipes and redirections inside command chains are not supported (yet).

**Currently Supported Features:**
- Runs commands (ofc)
- cd comamnd
- time command for measuring how long a command takes to finish.
- Pipes
- Redirections (Both > and >>)
- Multiple Command Chaining

Bugs:
- I know there is a ton of bugs but there are some I plan on fixing and some I will not.
