import argparse
import os
import pty
import select
import sys
import time

from multiprocessing import Process
from tempfile import NamedTemporaryFile
from vtpy import SerialTerminal, Terminal, TerminalException


def spawnTerminal(port: str, baudrate: int, flow: bool) -> Terminal:
    print("Attempting to contact VT-100...", end="")
    sys.stdout.flush()

    while True:
        try:
            # The serial terminal class will only return successfully if the terminal
            # is awake and responding properly, including a terminal identification and
            # okay response.
            terminal = SerialTerminal(port, baudrate, flowControl=flow)
            print("SUCCESS!")

            break
        except TerminalException:
            # Wait for terminal to re-awaken.
            time.sleep(1.0)

            print(".", end="")
            sys.stdout.flush()

    # We have a handle to an actual terminal here.
    return terminal


def ptyProcess(process: str, stdin: int, stdout: int) -> None:
    # The pty module only takes processes to run. If we want to take an arbitrary shell
    # command to run instead, then we need to write that to a temporary script, chmod
    # it to writeable, and then pass that script to pty. So, we do that here.
    scriptFile = NamedTemporaryFile(delete=True)
    with open(scriptFile.name, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write(f"{process}\n")

    os.chmod(scriptFile.name, 0o777)
    scriptFile.file.close()

    # Hook our own stdin/stdout/stderr to the pipes we were provided, since pty just
    # connects the spawned process to these. This kills this process's ability to output
    # its own errors, so let's hope nothing ever crashes here.
    os.dup2(stdin, 0)
    os.dup2(stdout, 1)
    os.dup2(stdout, 2)
    os.putenv("TERM", "vt100")
    pty.spawn(scriptFile.name)


def main(command: str, port: str, baudrate: int, flow: bool) -> int:
    # First, contact the terminal and then clear it.
    terminal = spawnTerminal(port, baudrate, flow)
    terminal.reset()

    # Now, create a two-way pipe for communications.
    (stdinr, stdinw) = os.pipe()
    (stdoutr, stdoutw) = os.pipe()

    # Now, fork off a process for the pty to run the command without messing
    # up our own terminal output. Also, we want to be able to poll the terminal
    # so we need to be in a different thread/process anyway.
    p = Process(target=ptyProcess, args=(command, stdinr, stdoutw))
    p.start()

    # Now, loop forever reading/writing from the terminal to the stdin/stdout.
    print("Starting monitoring!")
    while True:
        # First, check if we're done. If join succeeds then we won't be alive, and we should
        # bail out of the loop. Most likely the user exited the process on the terminal.
        p.join(timeout=0)
        if not p.is_alive():
            print("Finished monitoring!")
            break

        # Now, check for if there's something to do by seeing if there's anything to read. We
        # select so we don't get stuck polling forever if the command we're running hasn't output
        # anything.
        r, w, e = select.select([stdoutr], [], [], 0)
        if stdoutr in r:
            data = os.read(stdoutr, 128)
            terminal.interface.write(data)

        while True:
            # Now, while we get more than zero bytes back from the terminal, relay those to the
            # process we spawned.
            val = terminal.interface.read()
            if val:
                # Get rid of \r\n that the terminal sends on "RETURN", make it act the same
                # as "LINE FEED" and stop duplicating prompts.
                val = bytes([x for x in val if x != 13])
                os.write(stdinw, val)
            else:
                break

    # Clean up, clean up, everybody everywhere! Clean up, clean up, everybody do your share!
    os.close(stdinr)
    os.close(stdinw)
    os.close(stdoutr)
    os.close(stdoutw)
    terminal.reset()

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="VT-100 terminal proxy")

    parser.add_argument(
        "--port",
        default="/dev/ttyUSB0",
        type=str,
        help="Serial port to open, defaults to /dev/ttyUSB0",
    )
    parser.add_argument(
        "--baud",
        default=9600,
        type=int,
        help="Baud rate to use with VT-100, defaults to 9600",
    )
    parser.add_argument(
        "--flow",
        action="store_true",
        help="Enable software-based flow control (XON/XOFF)",
    )
    parser.add_argument(
        "--command",
        default="/bin/bash",
        type=str,
        help="Command to execute, proxying stdin/stdout/stderr to the terminal",
    )
    args = parser.parse_args()

    sys.exit(main(args.command, args.port, args.baud, args.flow))
