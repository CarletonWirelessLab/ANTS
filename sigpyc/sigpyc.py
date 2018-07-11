#!/usr/bin/python3

from PyQt5.QtWidgets import QWidget, QCheckBox, QApplication, QComboBox, QMessageBox, QPushButton, QMainWindow, QLineEdit, QSlider, QLabel
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
import sys
import subprocess
import threading
import time
import queue
import os
import matlab.engine

# WiFiQt implements support for semi-automated test runs using an USRP and
# other high-frequency I/O devices. The GUI is written entirely using PyQt5.
# Once everything is in a working, deployable state, the GUI and functional
# aspects need to be separated for modularity purposes
class SiGPyC(QMainWindow):

    def __init__(self, test_mode=False):
        super().__init__()

        # Class variables that are set by toggling the checkboxes. Used to
        # determine which tools to run when the "Run" button is pressed
        self.usrp_state = False
        self.controller_state = False
        self.converter_state = False
        self.plotter_state = False
        self.iperf_state = False

        # Class variables used for the subprocesses run, if any, of the tools
        # run when their checkboxes are selected
        self.usrp_proc = None
        self.controller_proc = None
        self.converter_proc = None
        self.plotter_proc = None
        self.iperf_client_proc = None
        self.iperf_server_proc = None

        # Buffer lists for the queue utilization. Not used, will likely be
        # removed in the future
        self.usrp_buffer = []
        self.controller_buffer = []
        self.converter_buffer = []
        self.plotter_buffer = []
        self.iperf_buffer = []

        # Queues for each tool. Not used, will likely be removed in the future
        self.usrp_queue = queue.Queue()
        self.controller_queue = queue.Queue()
        self.converter_queue = queue.Queue()
        self.plotter_queue = queue.Queue()
        self.iperf_queue = queue.Queue()

        # Thread variables for reading from queued processes as they run. Not
        # used, will likely be removed in the future
        self.usrp_thread = None
        self.controller_thread = None

        # iperf-specific variables. The client_addr and server_addr variables
        # are self-explanatory and are set from the GUI's lineedit boxes.
        # Rate and mem_addr are for the other inputs to the client call
        # iperf -c [IP] -u -b[100]M -S [0x00]  -t10000000000
        self.iperf_client_addr = None
        self.iperf_server_addr = None
        self.iperf_rate = None
        self.iperf_mem_addr = None

        # Ensure that a proper IP format is used. Taken from
        # https://evileg.com/en/post/57/
        self.ip_range = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        self.ip_regex = QRegExp("^" + self.ip_range + "\\." + self.ip_range + "\\." + self.ip_range + "\\." + self.ip_range + "$")
        self.ip_validator = QRegExpValidator(self.ip_regex, self)

        # Default run time length
        self.run_time = 0.5

        # Output/conversion file name
        self.file_name = ""

        # Flag used to tell the program that it's in test mode or not
        self.test_mode = test_mode

        # matlab.engine is the Python wrapper for calling Matlab scripts and
        # functions. The entire local path and its subdirectories must be added
        # to the workspace to ensure that the converter and plotter tools work
        print("Starting Matlab engine for Python... ")
        self.engine = matlab.engine.start_matlab()
        print("Done\n")

        print("Pre-cleaning workspace...")
        self.engine.close('all', nargout=0)
        self.engine.clear('all', nargout=0)
        print("Done\n")
        print("Setting up Matlab engine workspace...")
        cur_dir = os.getcwd()
        self.engine.addpath(self.engine.genpath(cur_dir))
        print("Done\n")

        # Starts up the UI
        self.init_UI()


    # The primary method for setting up the buttons and other widgets, including
    # the arguments to be run using subprocess.Popen()
    def init_UI(self):

        self.statusBar().showMessage('Idle')

        # Each of these targets a local test script that prints a
        # self-identification message, then runs time.sleep() for a certain
        # amount of seconds
        if self.test_mode == True:
            self.usrp_control_args = ["python3", "../tests/fake_USRP_control.py"]
            self.sg_controller_args = ["python3", "../tests/fake_SG_control.py"]
            self.matlab_converter_args = ["python3", "../tests/fake_matlab_converter.py"]
            self.matlab_plotter_args = ["python3", "../tests/fake_matlab_plotter.py"]

        # Run the real arguments in the intended environment. using
        # subprocess.Popen() Note that writeIQ still needs to have support for
        # variable run time added before the slider in the GUI has any effect
        else:
            self.usrp_control_args = ["python", "../utils/writeIQ.py", "123", str(self.run_time)]
            self.sg_controller_args = ["python3", "./utils/rnd_control.py", str(self.run_time)]

        # The arguments to give to subprocess.Popen() to run iperf
        self.iperf_client_args = ["iperf", "-c", str(self.iperf_client_addr), "-u", "-b"+str(self.iperf_rate)+"M", "-S", str(self.iperf_mem_addr), "-t10000000000"]
        self.iperf_server_args = ["iperf", "-s", "-u", "-t100000000000000"]

        # The checkbox for enabling the USRP
        usrp_checkbox = QCheckBox('USRP', self)
        usrp_checkbox.move(20, 20)
        usrp_checkbox.stateChanged.connect(self.usrp_check)

        # The checkbox for enabling the signal generator, if used
        controller_checkbox = QCheckBox('SGControl', self)
        controller_checkbox.move(20, 80)
        controller_checkbox.stateChanged.connect(self.controller_check)

        # The checkbox for the conversion tool
        converter_checkbox = QCheckBox('Convert', self)
        converter_checkbox.move(20, 140)
        converter_checkbox.stateChanged.connect(self.converter_check)

        # The checkbox for the plotting tool
        plotter_checkbox = QCheckBox('Plot', self)
        plotter_checkbox.move(20, 200)
        plotter_checkbox.stateChanged.connect(self.plotter_check)

        # The checkbox for running iperf
        iperf_checkbox = QCheckBox('iperf', self)
        iperf_checkbox.move(20, 260)
        iperf_checkbox.stateChanged.connect(self.iperf_check)

        # Labels for the iperf IP address boxes
        iperf_client_label = QLabel("Client IP", self)
        iperf_client_label.move(20, 300)
        iperf_server_label = QLabel("Server IP", self)
        iperf_server_label.move(20, 360)

        # Create text boxes that use the regex rules and ip_validator from
        # above to ensure that proper IP addresses for the devices are given
        self.iperf_client_lineedit = QLineEdit(self)
        self.iperf_client_lineedit.setValidator(self.ip_validator)
        self.iperf_client_lineedit.textChanged[str].connect(self.on_client_ip)
        self.iperf_client_lineedit.move(20, 325)
        self.iperf_server_lineedit = QLineEdit(self)
        self.iperf_server_lineedit.setValidator(self.ip_validator)
        self.iperf_server_lineedit.textChanged[str].connect(self.on_server_ip)
        self.iperf_server_lineedit.move(20, 385)

        # Create a text box to take the filename used by the USRP and converter
        # tools
        self.file_name_lineedit = QLineEdit(self)
        self.file_name_lineedit.textChanged[str].connect(self.on_name_change)
        self.file_name_lineedit.move(380, 125)
        self.file_name_text = "Filename"
        self.file_name_label = QLabel(self.file_name_text, self)
        self.file_name_label.move(380, 100)
        # self.file_name_set_button = QPushButton('Set', self)
        # self.file_name_set_button.setToolTip('Set the target filename')
        # self.file_name_set_button.resize(self.file_name_set_button.sizeHint())
        # self.file_name_set_button.move(380, 160)



        # Run time slider set up. Currently does nothing until the writeIQ
        # program supports run time input
        self.runtime_slider = QSlider(Qt.Horizontal, self)
        self.runtime_slider.setFocusPolicy(Qt.NoFocus)
        self.runtime_slider.setGeometry(380,70,100,30)
        self.runtime_slider.valueChanged[int].connect(self.change_value)
        self.runtime_slider.setMinimum(0)
        self.runtime_slider.setMaximum(20)
        self.runtime_slider.setTickInterval(1)
        self.runtime_text = str(0.5) + " seconds"
        self.runtime_label = QLabel(self.runtime_text, self)
        self.runtime_label.move(380, 50)

        # The button for running the entire sequence
        run_btn = QPushButton('Run', self)
        run_btn.setToolTip('Run the test sequences selected')
        run_btn.resize(run_btn.sizeHint())
        run_btn.move(380, 20)
        run_btn.clicked.connect(self.run_button_clicked)

        # The following two button setups do nothing at the moment. They are
        # kept for example usage and for future expansion

        # controller_setup_btn = QPushButton('Controller Settings', self)
        # controller_setup_btn.setToolTip('Modify signal generator parameters')
        # controller_setup_btn.resize(controller_setup_btn.sizeHint())
        # controller_setup_btn.move(345, 100)

        # test_setup_btn = QPushButton('Test Settings', self)
        # test_setup_btn.setToolTip('Modify test setup and parameters')
        # test_setup_btn.resize(test_setup_btn.sizeHint())
        # test_setup_btn.move(380, 160)

        #controller_setup_btn.clicked.connect(self.controller_button_clicked)
        #test_setup_btn.clicked.connect(self.test_button_clicked)

        # Set up the GUI window
        self.setGeometry(300, 600, 500, 500)
        self.setWindowTitle('SYSC WiFi Control Panel')
        self.show()

    # Changes the usrp run state when the checkbox is clicked
    def usrp_check(self, state):

        if state == Qt.Checked:
            self.usrp_state = True
        else:
            self.usrp_state = False

    # Changes the controller run state when the checkbox is clicked
    def controller_check(self, state):

        if state == Qt.Checked:
            self.controller_state = True
        else:
            self.controller_state = False

    # Changes the converter run state when the checkbox is clicked
    def converter_check(self, state):

        if state == Qt.Checked:
            self.converter_state = True
        else:
            self.converter_state = False

    # Changes the plotter run state when the checkbox is clicked
    def plotter_check(self, state):

        if state == Qt.Checked:
            self.plotter_state = True
        else:
            self.plotter_state = False

    # Changes the iperf run state when the checkbox is clicked
    def iperf_check(self, state):

        if state == Qt.Checked:
            self.iperf_state = True
        else:
            self.iperf_state = False

    # Controls changing the value pointed to by the slider. The slider should
    # allow ranges between 0.5 and 10, but since the class only supports
    # integers, some math must be done to the actual value when it is moved
    def change_value(self, value):

        if value == 0:
            self.run_time = 0.5
        elif value == 20:
            self.run_time = 10
        else:
            self.run_time = value / 2.0
        self.runtime_label.setText(str(self.run_time) + " seconds")

    # Checks to make sure iperf_client_addr is set to a realistic IP value
    def on_client_ip(self, text):

        if self.iperf_client_lineedit.hasAcceptableInput():
            self.iperf_client_addr = text

    # Checks to make sure iperf_server_addr is set to a realistic IP value
    def on_server_ip(self, text):

        if self.iperf_server_lineedit.hasAcceptableInput():
            self.iperf_server_addr = text

    # Set file name based on what's in the box
    def on_name_change(self, text):

        self.file_name = text


    # Runs a subprocess for the USRP based on the usrp_control_args variable
    def start_usrp(self):
        print("Running USRP...\n")
        self.usrp_control_args = ["python", "../utils/writeIQ.py", self.file_name, str(self.run_time)]
        self.usrp_proc = subprocess.Popen(self.usrp_control_args, stdin=subprocess.PIPE, stderr=None, shell=False)
        while self.usrp_proc.poll() is None:
            continue
        print("Done sensing medium\n")

        return
    # Runs a subprocess for the SGControl tool based on the sg_controller_args
    # variable
    def start_controller(self, args):
        print("Running interference...\n")
        self.controller_proc = subprocess.Popen(self.sg_controller_args, stdin=subprocess.PIPE, stderr=None, shell=False)
        while self.controller_proc.poll() is None:
            continue
        print("Done injecting interference\n")

        return

    # Runs the USRP and SGControl tools simultaneously if and only if both boxes
    # are checked
    def start_usrp_controller(self):
        print("Running USRP with interference injected...\n")
        self.usrp_control_args = ["python", "../utils/writeIQ.py", self.file_name, str(self.run_time)]
        self.usrp_proc = subprocess.Popen(self.usrp_control_args, stdin=subprocess.PIPE, stderr=None, shell=False)
        self.controller_proc = subprocess.Popen(self.sg_controller_args, stdin=subprocess.PIPE, stderr=None, shell=False)

        while True:

            self.usrp_proc.poll()
            self.controller_proc.poll()
            # Make sure the sequence won't continue until both tools have
            # finished
            if self.usrp_proc.returncode is not None or self.controller_proc.returncode is not None:
                break

        print("Done sensing with added interference\n")
        return

    # Runs the USRP and iperf tools simultaneously if and only if both boxes
    # are checked
    def start_usrp_iperf(self):
        print("Running USRP with interference injected...\n")
        self.usrp_control_args = ["python", "../utils/writeIQ.py", self.file_name, str(self.run_time)]
        self.usrp_proc = subprocess.Popen(self.usrp_control_args, stdin=subprocess.PIPE, stderr=None, shell=False)
        self.iperf_client_proc = subprocess.Popen(self.iperf_client_args, stdin=subprocess.PIPE, stderr=None, shell=False)
        self.iperf_server_proc = subprocess.Popen(self.iperf_server_args, stdin=subprocess.PIPE, stderr=None, shell=False)

        while True:

            self.usrp_proc.poll()
            self.iperf_client_proc.poll()
            self.iperf_server_proc.poll()
            # Make sure the sequence won't continue until all tools have
            # finished
            if self.usrp_proc.returncode is not None or self.iperf_client_proc.returncode is not None or self.iperf_server_proc.returncode is not None:
                break

        print("Done sensing with iperf\n")
        return


    # Run the matlab function to convert the collected data
    # def start_converter(self, args):
    #     print("Running converter tool...\n")
    #     if self.test_mode == True:
    #         self.converter_proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
    #         while self.converter_proc.poll() is None:
    #             continue
    #     else:
    #         matlab.engine.displayTimingInformation()
    #     print("Done conversion\n")
    #
    #     return

    def start_converter(self):
        print("Running converter tool...\n")
        print(self.file_name)
        self.engine.workspace['fileName'] = self.file_name + ".bin"
        self.engine.displayTimingInformation(nargout=0)
        #self.engine.run('displayTimingInformation.m', nargout=0)
        print("Done conversion\n")

    # Run the matlab function to plot the converted data
    # def start_plotter(self, args):
    #     print("Running plotter...\n")
    #     if self.test_mode == True:
    #         self.plotter_proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
    #         while self.plotter_proc.poll() is None:
    #             continue
    #     else:
    #         matlab.engine.Load_and_Eval()
    #     print("Done plotting\n")
    #
    #     return
    def start_plotter(self):
        print("Running plotter...\n")
        self.engine.Load_and_Eval(nargout=0)
        print("Done plotting\n")

    # Runs the iperf client and server processes
    def start_iperf(self):
        print("Running iperf...\n")
        self.iperf_client_proc = subprocess.Popen(self.iperf_client_args, stdin=subprocess.PIPE, stderr=None, shell=False)
        self.iperf_server_proc = subprocess.Popen(self.iperf_server_args, stdin=subprocess.PIPE, stderr=None, shell=False)

        while True:

            self.iperf_client_proc.poll()
            self.iperf_server_proc.poll()
            # Make sure the sequence won't continue until both tools have
            # finished. Is it necessary that we wait for the server, or is the
            # time given to it just to ensure that we had time to run the client
            # manually?
            if self.iperf_client_proc.returncode is not None or self.iperf_server_proc.returncode is not None:
                break

        print("Done running iperf\n")
        return

    # The logic for when the "Run" button is pressed. It checks to see which
    # boxes are checked, then runs based on what it sees. Is there a case where
    # we don't want to run the USRP? Should make this more modular, turn it
    # into a dictionary with functions as the values
    def run_button_clicked(self, options):
        sender = self.sender()
        self.statusBar().showMessage('Running...')

        # USRP, iperf, Converter, Plotter
        if (self.usrp_state and self.iperf_state and self.converter_state and self.plotter_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.iperf_state), str(self.converter_state), str(self.plotter_state)))
            self.start_usrp_iperf()
            self.start_converter()
            self.start_plotter()

        # USRP, SGControl, Converter
        elif (self.usrp_state and self.controller_state and self.converter_state and not self.plotter_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_usrp_controller()
            self.start_converter()

        # USRP, iperf, Converter
        elif (self.usrp_state and self.iperf_state and self.converter_state and not self.plotter_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_usrp_iperf()
            self.start_converter()

        # USRP, Converter, Plotter
        elif (self.usrp_state and self.converter_state and self.plotter_state and not self.controller_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_usrp()
            self.start_converter()
            self.start_plotter()

        # USRP, SGControl
        elif (self.usrp_state and self.controller_state and not self.converter_state and not self.plotter_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_usrp_controller()

        # USRP, iperf
        elif (self.usrp_state and self.iperf_state and not self.converter_state and not self.plotter_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_usrp_iperf()

        # USRP only
        elif (self.usrp_state and not self.controller_state and not self.converter_state and not self.plotter_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_usrp()

        # SGControl only
        elif (self.controller_state and not self.usrp_state and not self.converter_state and not self.plotter_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_controller()

        elif (self.usrp_state and self.converter_state and not self.plotter_state and not self.controller_state and not self.iperf_state):

            self.start_usrp()
            self.start_converter()

        # Converter and Plotter
        elif (self.converter_state and self.plotter_state and not self.usrp_state and not self.controller_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_converter()
            self.start_plotter()

        # Converter only
        elif (self.converter_state and not self.usrp_state and not self.plotter_state and not self.controller_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_converter()

        # Plotter only
        elif (self.plotter_state and not self.converter_state and not self.usrp_state and not self.controller_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_plotter()

        elif (self.iperf_state and not self.converter_state and not self.usrp_state and not self.controller_state and not self.plotter_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.iperf_state), str(self.converter_state), str(self.plotter_state)))
            self.start_iperf()

        # What did you select?
        else:
            print("No options or bad options given\n")

        self.statusBar().showMessage('Idle')


    # def controller_button_clicked(self):
    #     sender = self.sender()
    #     print("Controller button pressed\n")

    # def test_button_clicked(self):
    #     sender = self.sender()
    #     print("Test button pressed\n")

    # Unused function for reading the pipe outputs when the code relied on
    # queues for the USRP and SGControl tools
    def read_pipe_output(self, pipe, queue):

        while True:
            line = pipe.readline()
            queue.put(line)

    # Make sure we get prompted before closing the GUI
    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
            "Are you sure you want to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

# What to do when this file is called
if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = SiGPyC()
    sys.exit(app.exec_())
