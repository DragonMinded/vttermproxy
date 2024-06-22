# vttermproxy

A simple proxy that acts as a terminal, but allows you to use the pyvt module to talk to a VT-100 without forcing your serial terminal to be a pty on linux. Whatever command is provided inside the command argument will be executed as a shell script with the stdin hooked to the terminal's keyboard, and the stdout and stderr hooked to the terminal's display. This means that the command will run with it's output sent to the VT-100, and input from the VT-100 keyboard will be sent to the command. As a convenience, before launching the command, the `TERM` environment variable is set to `vt100` so most commands will just work out of the box. Because this presents the program a real terminal interface, commands such as sudo will work when wrapped with this.

## Running This

If you are non-technical, or you just want to try it out without tinkering, I recommend using `pipx` to install the vttermproxy. For help and instruction on setting up `pipx` on your computer, visit [pipx's installation page](https://pipx.pypa.io/stable/installation/). If you have `pipx` installed already, run the following line to install vttermproxy on your computer.

```
pipx install git+https://github.com/DragonMinded/vttermproxy.git
```

Once that completes, you can run this proxy by typing the following line, substituting your command:

```
vttermproxy --command "<your proxied command here>"
```

You can also run with `--help`, like the following example, to see all options:

```
vttermproxy --help
```

Note that original VT-100 terminals, and variants such as the 101 and 102, need the XON/XOFF flow control option enabled. Make sure you enable flow control on the terminal itself, and then use the `--flow` argument to avoid overloading the terminal. Newer terminals such as mid-80s VT-100 clones often do not suffer from this problem and keep up just fine.

## Development

To get started, first install the requirements using a command similar to:

```
python3 -m pip install -r requirements.txt
python3 -m pip install -r requirements-dev.txt
```

Then, you can run the application similar to:

```
python3 vttermproxy --command "<your proxied command here>"
```

You can also run with `--help`, like the following example, to see all options:

```
python3 vttermproxy --help
```
