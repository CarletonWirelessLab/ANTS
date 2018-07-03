#!/usr/bin/python3

from PyQt5.QtWidgets import QWidget, QCheckBox, QApplication, QComboBox, QMessageBox, QPushButton, QMainWindow, QLineEdit, QSlider, QLabel
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
import sys
import subprocess
import threading
import time
import queue
import matlab.engine as matlab

class WiFiQt(QMainWindow):

    def __init__(self, test_mode=False):
        super().__init__()

        self.usrp_state = False
        self.controller_state = False
        self.converter_state = False
        self.plotter_state = False
        self.iperf_state = False

        self.usrp_proc = None
        self.controller_proc = None
        self.converter_proc = None
        self.plotter_proc = None
        self.iperf_proc = None

        self.usrp_buffer = []
        self.controller_buffer = []
        self.converter_buffer = []
        self.plotter_buffer = []
        self.iperf_buffer = []

        self.usrp_queue = queue.Queue()
        self.controller_queue = queue.Queue()
        self.converter_queue = queue.Queue()
        self.plotter_queue = queue.Queue()
        self.iperf_queue = queue.Queue()

        self.usrp_thread = None
        self.controller_thread = None

        self.iperf_client_thread = None
        self.iperf_server_thread = None
        self.iperf_client_addr = None
        self.iperf_server_addr = None
        self.iperf_rate = None
        self.iperf_mem_addr = None

        # Ensure that a proper IP format is used. Taken from https://evileg.com/en/post/57/
        self.ip_range = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        self.ip_regex = QRegExp("^" + self.ip_range + "\\." + self.ip_range + "\\." + self.ip_range + "\\." + self.ip_range + "$")
        self.ip_validator = QRegExpValidator(self.ip_regex, self)

        # Default run time length
        self.run_time = 0.5

        self.init_UI()


    def init_UI(self):

        self.statusBar().showMessage('Idle')

        if test_mode == True:
            self.usrp_control_args = ["python3", "./fake_USRP_control.py"]
            self.sg_controller_args = ["python3", "./fake_SG_control.py"]
            self.matlab_converter_args = ["python3", "./fake_matlab_converter.py"]
            self.matlab_plotter_args = ["python3", "./fake_matlab_plotter.py"]
        else:
            self.usrp_control_args = ["python", "./writeIQ.py"]
            self.sg_controller_args = ["python3", "./rnd_control.py"]

        self.iperf_client_args = ["iperf", "-c", str(self.iperf_client_addr), "-u", "-b"+str(self.iperf_rate)+"M", "-S", str(self.iperf_mem_addr), "-t10000000000"]
        self.iperf_server_args = ["iperf", "-s", "-u", "-t100000000000000"]

        usrp_checkbox = QCheckBox('USRP', self)
        usrp_checkbox.move(20, 20)
        usrp_checkbox.stateChanged.connect(self.usrp_check)

        controller_checkbox = QCheckBox('SGControl', self)
        controller_checkbox.move(20, 80)
        controller_checkbox.stateChanged.connect(self.controller_check)

        converter_checkbox = QCheckBox('Convert', self)
        converter_checkbox.move(20, 140)
        converter_checkbox.stateChanged.connect(self.converter_check)

        plotter_checkbox = QCheckBox('Plot', self)
        plotter_checkbox.move(20, 200)
        plotter_checkbox.stateChanged.connect(self.plotter_check)

        iperf_checkbox = QCheckBox('iperf', self)
        iperf_checkbox.move(20, 260)
        iperf_checkbox.stateChanged.connect(self.iperf_check)

        iperf_client_label = QLabel("Client IP Address", self)
        iperf_client_label.move(20, 300)
        iperf_server_label = QLabel("Server IP Address", self)
        iperf_server_label.move(20, 360)

        self.iperf_client_lineedit = QLineEdit(self)
        self.iperf_client_lineedit.setValidator(self.ip_validator)
        self.iperf_client_lineedit.textChanged[str].connect(self.on_client_ip)
        self.iperf_client_lineedit.move(20, 325)
        self.iperf_server_lineedit = QLineEdit(self)
        self.iperf_server_lineedit.setValidator(self.ip_validator)
        self.iperf_server_lineedit.textChanged[str].connect(self.on_server_ip)
        self.iperf_server_lineedit.move(20, 385)


        # Runtime slider set up
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

        self.setGeometry(300, 600, 500, 500)
        self.setWindowTitle('SYSC WiFi Control Panel')
        self.show()


    def usrp_check(self, state):

        if state == Qt.Checked:
            self.usrp_state = True
        else:
            self.usrp_state = False

    def controller_check(self, state):

        if state == Qt.Checked:
            self.controller_state = True
        else:
            self.controller_state = False

    def converter_check(self, state):

        if state == Qt.Checked:
            self.converter_state = True
        else:
            self.converter_state = False

    def plotter_check(self, state):

        if state == Qt.Checked:
            self.plotter_state = True
        else:
            self.plotter_state = False

    def iperf_check(self, state):

        if state == Qt.Checked:
            self.iperf_state = True
        else:
            self.iperf_state = False

    # The slider should allow ranges between 0.5 and 10, but since the class
    # only supports integers, some math must be done to the actual value when
    # it is moved
    def change_value(self, value):

        if value == 0:
            self.run_time = 0.5
        elif value == 20:
            self.run_time = 10
        else:
            self.run_time = value / 2.0
        self.runtime_label.setText(str(self.run_time) + " seconds")

    def on_client_ip(self, text):

        if self.iperf_client_lineedit.hasAcceptableInput():
            self.iperf_client_addr = text

    def on_server_ip(self, text):

        if self.iperf_server_lineedit.hasAcceptableInput():
            self.iperf_server_addr = text



    def start_usrp(self, args):
        print("Running USRP...\n")
        self.usrp_proc = subprocess.Popen(args, stdin=subprocess.PIPE, stderr=None, shell=False)
        while self.usrp_proc.poll() is None:
            continue
        print("Done sensing medium\n")

        return

    def start_controller(self, args):
        print("Running interference...\n")
        self.controller_proc = subprocess.Popen(args, stdin=subprocess.PIPE, stderr=None, shell=False)
        while self.controller_proc.poll() is None:
            continue
        print("Done injecting interference\n")

        return

    def start_usrp_controller(self, usrp_args, controller_args):
        print("Running USRP with interference injected...\n")
        self.usrp_proc = subprocess.Popen(usrp_args, stdin=subprocess.PIPE, stderr=None, shell=False)
        self.controller_proc = subprocess.Popen(controller_args, stdin=subprocess.PIPE, stderr=None, shell=False)

        while True:

            self.usrp_proc.poll()
            self.controller_proc.poll()

            if self.usrp_proc.returncode is not None or self.controller_proc.returncode is not None:
                break

        print("Done sensing with added interference\n")
        return



    def start_converter(self, args):
        print("Running converter tool...\n")
        self.converter_proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
        while self.converter_proc.poll() is None:
            continue
        print("Done conversion\n")

        return

    def start_plotter(self, args):
        print("Running plotter...\n")
        self.plotter_proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
        while self.plotter_proc.poll() is None:
            continue
        print("Done plotting\n")

        return

    def run_button_clicked(self, options):
        sender = self.sender()
        self.statusBar().showMessage('Running...')

        # All options checked
        if (self.usrp_state and self.controller_state and self.converter_state and self.plotter_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_usrp_controller(self.usrp_control_args, self.sg_controller_args)
            self.start_converter(self.matlab_converter_args)
            self.start_plotter(self.matlab_plotter_args)

        # USRP, SGControl, Converter
        elif (self.usrp_state and self.controller_state and self.converter_state and not self.plotter_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_usrp_controller(self.usrp_control_args, self.sg_controller_args)
            self.start_converter(self.matlab_converter_args)

        # Controller, Converter, Plotter
        elif (self.controller_state and self.converter_state and self.plotter_state and not self.usrp_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_controller(self.sg_controller_args)
            self.start_converter(self.matlab_converter_args)
            self.start_plotter(self.matlab_plotter_args)

        # USRP, Converter, Plotter
        elif (self.usrp_state and self.converter_state and self.plotter_state and not self.controller_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_usrp(self.usrp_control_args)
            self.start_converter(self.matlab_converter_args)
            self.start_plotter(self.matlab_plotter_args)

        # USRP, SGControl
        elif (self.usrp_state and self.controller_state and not self.converter_state and not self.plotter_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_usrp_controller(self.usrp_control_args, self.sg_controller_args)

        # USRP only
        elif (self.usrp_state and not self.controller_state and not self.converter_state and not self.plotter_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_usrp(self.usrp_control_args)

        # SGControl only
        elif (self.controller_state and not self.usrp_state and not self.converter_state and not self.plotter_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_controller(self.sg_controller_args)

        # Converter and Plotter
        elif (self.converter_state and self.plotter_state and not self.usrp_state and not self.controller_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_converter(self.matlab_converter_args)
            self.start_plotter(self.matlab_plotter_args)

        # Converter only
        elif (self.converter_state and not self.usrp_state and not self.plotter_state and not self.controller_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_converter(self.matlab_converter_args)

        # Plotter only
        elif (self.plotter_state and not self.converter_state and not self.usrp_state and not self.controller_state):

            print("{0} {1} {2} {3}\n".format(str(self.usrp_state), str(self.controller_state), str(self.converter_state), str(self.plotter_state)))
            self.start_plotter(self.matlab_plotter_args)

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

    def read_pipe_output(self, pipe, queue):

        while True:
            line = pipe.readline()
            queue.put(line)

    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
            "Are you sure you want to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = WiFiQt()
    sys.exit(app.exec_())
