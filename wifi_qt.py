#!/usr/bin/python3

from PyQt5.QtWidgets import QWidget, QCheckBox, QApplication, QComboBox, QMessageBox, QPushButton
from PyQt5.QtCore import Qt
import sys
import subprocess
import threading
import time
import queue

class WiFiQt(QWidget):

    def __init__(self):
        super().__init__()

        self.usrp_state = False
        self.controller_state = False
        self.converter_state = False
        self.plotter_state = False

        self.usrp_proc = None
        self.controller_proc = None
        self.converter_proc = None
        self.plotter_proc = None

        self.usrp_buffer = []
        self.controller_buffer = []
        self.converter_buffer = []
        self.plotter_buffer = []

        self.usrp_queue = queue.Queue()
        self.controller_queue = queue.Queue()
        self.converter_queue = queue.Queue()
        self.plotter_queue = queue.Queue()

        self.usrp_thread = None
        self.controller_thread = None

        self.init_UI()


    def init_UI(self):

        #self.usrp_control_args = ["python3", "./fake_USRP_control.py"]
        self.usrp_control_args = ["python", "./writeIQ.py"]
        #self.sg_controller_args = ["python3", "./fake_SG_control.py"]
        self.sg_controller_args = ["python3", "./rnd_control.py"]
        self.matlab_converter_args = ["python3", "./fake_matlab_converter.py"]
        self.matlab_plotter_args = ["python3", "./fake_matlab_plotter.py"]

        usrp_checkbox = QCheckBox('Run USRP', self)
        usrp_checkbox.move(20, 20)
        usrp_checkbox.stateChanged.connect(self.usrp_check)

        controller_checkbox = QCheckBox('Run Signal Generator', self)
        controller_checkbox.move(20, 80)
        controller_checkbox.stateChanged.connect(self.controller_check)

        converter_checkbox = QCheckBox('Run Converter', self)
        converter_checkbox.move(20, 140)
        converter_checkbox.stateChanged.connect(self.converter_check)

        plotter_checkbox = QCheckBox('Run Plotter', self)
        plotter_checkbox.move(20, 200)
        plotter_checkbox.stateChanged.connect(self.plotter_check)

        run_btn = QPushButton('Run', self)
        run_btn.setToolTip('Run the test sequences selected')
        run_btn.resize(run_btn.sizeHint())
        run_btn.move(380, 20)

        controller_setup_btn = QPushButton('Controller Settings', self)
        controller_setup_btn.setToolTip('Modify signal generator parameters')
        controller_setup_btn.resize(controller_setup_btn.sizeHint())
        controller_setup_btn.move(345, 80)

        test_setup_btn = QPushButton('Test Settings', self)
        test_setup_btn.setToolTip('Modify test setup and parameters')
        test_setup_btn.resize(test_setup_btn.sizeHint())
        test_setup_btn.move(380, 140)

        run_btn.clicked.connect(self.run_button_clicked)
        controller_setup_btn.clicked.connect(self.controller_button_clicked)
        test_setup_btn.clicked.connect(self.test_button_clicked)

        self.setGeometry(300, 600, 500, 300)
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

        #self.usrp_thread = threading.Thread(target=self.read_pipe_output, args=(self.usrp_proc.stdout, self.usrp_queue))
        #self.controller_thread = threading.Thread(target=self.read_pipe_output, args=(self.controller_proc.stdout, self.controller_queue))
        #self.usrp_thread.daemon = True
        #self.controller_thread.daemon = True
        #self.usrp_thread.start()
        #self.controller_thread.start()

        while True:

            self.usrp_proc.poll()
            self.controller_proc.poll()

            if self.usrp_proc.returncode is not None or self.controller_proc.returncode is not None:
                break

            #try:
            #     line = self.usrp_queue.get(False)
            #     sys.stdout.write("USRP control output: ")
            #     sys.stdout.write(str(line))
            #except queue.Empty:
            #     pass
            #
            #try:
            #     line = self.controller_queue.get(False)
            #     sys.stdout.write("SGControl control output: ")
            #     sys.stdout.write(str(line))
            #except queue.Empty:
            #     pass

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


    def controller_button_clicked(self):
        sender = self.sender()
        print("Controller button pressed\n")

    def test_button_clicked(self):
        sender = self.sender()
        print("Test button pressed\n")

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
