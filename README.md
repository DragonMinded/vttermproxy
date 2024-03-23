A simple proxy that acts as a terminal, but allows you to use the pyvt module to talk to a VT-100 without forcing your serial terminal to be a pty on linux. Whatever command is provided inside the command argument will be executed as a shell script with the stdin hooked to the terminal's keyboard, and the stdout and stderr hooked to the terminal's display. As a convenience, before launching the command, the `TERM` environment variable is set to `vt100` so most commands will just work out of the box. Because this presents the program a real terminal interface, commands such as sudo will work when wrapped with this.
