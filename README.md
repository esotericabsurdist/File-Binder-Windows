#Executable File Binder

##For Windows
###Tested on Win7

This program takes multiple executable files and combines them into a single executable. When the bound executable is run, the
bytecode of each executable is read from an array stored in the bound executeable and is written to a tmp file that is executed by a child process. For each executable file you bind, a child is forked to run the executable.
This was based on another project of mine done for a security class.

##Usage:
```shell
python binder.py ./chrome.exe ./keyL0gg3r.exe
```

```shell
bound.exe
```
