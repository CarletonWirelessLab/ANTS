# SiGPyC

SiGPyC is a set of tools (written in Python 3) for the following:

1. Providing software triggers to a signal generator with remote-control capability such as the E4438C;
2. Doing so while simultaneously controlling other measurement equipment such as software-defined radios;
3. Testing such triggering tools locally (with simple server processes).

It will also serve as a set of examples of multithreading and other fun stuff.

The echo_server.py and echo_client.py scripts are based off of those found [here](https://pymotw.com/3/socket/tcp.html),
but they'll get improvements to be object-oriented as I go.

## Intended Usage

1. Run the echo_server.py script in one window
2. Pass arguments to the const_control.py script as necessary
3. Watch the fireworks

Currently both const_control.py and rnd_control.py are designed to be run by Python3 directly as executables, and have 
arguments hard-coded into their default operation modes. Therefore, the scripts must be modified manually to support
changes to settings such as run time or duty cycle. Later on, these options will be specified via command-line interface
and/or by GUI.
