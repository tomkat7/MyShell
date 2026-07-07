This is a very simple linux shell built in python. 
My goal is to learn how shells work, and the best way to do it is building one from scratch. 
I don't use the subprocess python library because then I wouldn't learn about proceses, forks etc.

## Use Instructions

**Installation:**
1) Download the `MyShell.zip`
2) Extract it
3) Make `mysh.py` it executable with `chmod +x mysh.py`
4) Run it with `./mysh.py`

**Things to know:**
- To exit, type `exit` and hit enter.
- When using pipes and redirections in the same command, the redirection has to be the last operation. 
- For background jobs, & must be the last thing in the command, and chains, time, and cd are not supported for background jobs. 

**Currently Supported Features:**
- Runs commands (ofc)
- cd comamnd
- time command for measuring how long a command takes to finish.
- Pipes
- Redirections (Both > and >>)
- Multiple Command Chaining
- Input Redirections
- ctrl+c to cancel running commands
- Background jobs


Bugs:
- I know there is a ton of bugs but there are some I plan on fixing and some I will not.
