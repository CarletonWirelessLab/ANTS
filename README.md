# SiGPyC

SiGPyC is tool written using Python 3 with PyQt5 to do the following:

1. Provide software triggers to a signal generator with remote-control capability such as the E4438C;
2. Doing so while simultaneously controlling other measurement equipment such as software-defined radios;
3. Automating conversion and plotting of sensed data;
4. Testing such triggering tools locally using simple server scripts (where possible and/or appropriate).

The echo_server.py and echo_client.py scripts are based off of those found [here](https://pymotw.com/3/socket/tcp.html),
but they'll get improvements to be object-oriented as I go.

## Intended Usage

1. Run the wifi_qt.py script by typing "python3 wifi_qt.py"
2. Toggle devices on or off, providing IP addresses and filenames as necessary
3. Watch the fireworks

## What Works

- USRP option
- Converter option
- Plotter option
- iperf option

## What Doesn't

- SGControl option (it actually does, but needs tweaks before it's ready for prime time)

## Requirements

SiGPyC should work on any modern Linux operating system with the following installed:

1. Python 3 (written and tested on 3.6.5)
2. PyQt5
3. MATLAB (used R2018a for testing)

Note that the code relies on the availability of the Python MATLAB Engine (installation instructions below). If MATLAB is unavailable then SiGPyC should still work, but it will be limited to controlling the USRP, signal generator, and iperf controls.

## Setup and Install

1. ```pip3 install pyqt5```
2. Navigate to /usr/local/MATLAB/R20XXX/extern/engines/python and run ``` sudo python3 setup.py install ```
3. ```git clone https://github.com/threexc/SiGPyC```

## To-Do List

1. Clean up the GUI and add more user-friendly features
2. Modularize the code (currently just one approximately 500-line script)
3. Add in original MATLAB code
4. Settings menus that allow the target devices to be configured (among other things), so that the USRP and signal generator paremeters are not hard-coded as they are now
5. Windows support

## Authors

* **Trevor Gamblin** - [threexc](https://github.com/threexc)
