# SiGPyC

SiGPyC is tool written using Python 3 with PyQt5 to do the following:

1. Provide software triggers to a signal generator or wireless device(s) with remote-control capability such as the E4438C;
2. Doing so while simultaneously controlling other measurement equipment such as software-defined radios;
3. Automating conversion and plotting of sensed data;
4. Testing such triggering tools locally using simple server scripts (where possible and/or appropriate).

The echo_server.py and echo_client.py scripts are based off of those found [here](https://pymotw.com/3/socket/tcp.html),
but they'll get improvements to be object-oriented as I go.

## Intended Usage

1. Change directory to utils/ and type "gcc lanio.c getopt.c -o ks_lanio"
2. Run the sigpyc.py main script by typing "python3 sigpyc/sigpyc.py" from the project directory
3. Toggle devices on or off, providing IP addresses and filenames as necessary
4. Watch the fireworks

## What Works

- USRP option
- SGControl option
- Converter option
- Plotter option

## What Doesn't

- iperf option (should work, but needs some more testing)

## Requirements

SiGPyC should work on any modern Linux operating system with the following installed:

1. Python 3 (written and tested on 3.6.5)
2. PyQt5
3. MATLAB (used R2018a for testing)
4. gnuradio (for the writeIQ script)

Note that the code relies on the availability of the Python MATLAB Engine (installation instructions below). If MATLAB is unavailable then SiGPyC should still work, but it will be limited to controlling the USRP, signal generator, and iperf controls.

## Setup and Install

1. ```pip3 install pyqt5```
2. ```sudo dnf install gnuradio```
3. Navigate to /usr/local/MATLAB/R20XXX/extern/engines/python and run ``` sudo python3 setup.py install ```
4. ```git clone https://github.com/threexc/SiGPyC```

## To-Do List

1. Clean up the GUI and add more user-friendly features
2. Settings menus that allow the target devices to be configured (among other things), so that the USRP and signal generator paremeters are not hard-coded as they are now
3. More configurability for the MATLAB scripts
4. Windows support (low-priority right now)

## Authors

* **Trevor Gamblin** - [threexc](https://github.com/threexc) - Primary developer
* **Ammar Alhosainy** - MATLAB and some Python tools
* **Kareem Attiah** - MATLAB and some Python tools
