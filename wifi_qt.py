#!/usr/bin/python3

from PyQt5.QtWidgets import QWidget, QCheckBox, QApplication, QComboBox, QMessageBox, QPushButton
from PyQt5.QtCore import Qt
import sys
import subprocess
import time

class WiFiQt(QWidget):

    def __init__(self):
        super().__init__()

        self.run_usrp = False
        self.run_controller = False
        self.run_converter = False
        self.run_plotter = False

        self.init_UI()


    def init_UI(self):

        # self.usrp_control_args = ["gnome-terminal", "-x", "python3", "fake_USRP_control.py"]
        # self.sg_controller_args = ["gnome-terminal", "-x", "python3", "fake_SG_control.py"]
        # self.matlab_converter_args = ["gnome-terminal", "-x", "python3", "fake_matlab_converter.py"]
        # self.matlab_plotter_args = ["gnome-terminal", "-x", "python3", "fake_matlab_plotter.py"]
        self.usrp_control_args = ["python3", "./fake_USRP_control.py"]
        self.sg_controller_args = ["python3", "./fake_SG_control.py"]
        self.matlab_converter_args = ["python3", "./fake_matlab_converter.py"]
        self.matlab_plotter_args = ["python3", "./fake_matlab_plotter.py"]

        usrp_checkbox = QCheckBox('Run USRP', self)
        usrp_checkbox.move(20, 20)
        #usrp_checkbox.toggle()
        usrp_checkbox.stateChanged.connect(self.usrp_check)

        controller_checkbox = QCheckBox('Run Signal Generator', self)
        controller_checkbox.move(20, 80)
        #controller_checkbox.toggle()
        usrp_checkbox.stateChanged.connect(self.controller_check)

        converter_checkbox = QCheckBox('Run Converter', self)
        converter_checkbox.move(20, 140)
        #converter_checkbox.toggle()
        converter_checkbox.stateChanged.connect(self.converter_check)

        plotter_checkbox = QCheckBox('Run Plotter', self)
        plotter_checkbox.move(20, 200)
        #plotter_checkbox.toggle()
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
            self.run_usrp = True
        else:
            self.run_usrp = False

    def controller_check(self, state):

        if state == Qt.Checked:
            self.run_controller = True
        else:
            self.run_controller = False

    def converter_check(self, state):

        if state == Qt.Checked:
            self.run_converter = True
        else:
            self.run_converter = False

    def plotter_check(self, state):

        if state == Qt.Checked:
            self.run_plotter = True
        else:
            self.run_plotter = False

    def run_button_clicked(self):
        sender = self.sender()
        print("Run button pressed\n")

        # All options checked
        if self.run_usrp and self.run_controller and self.run_converter and self.run_plotter:
            print("{0} {1} {2} {3}\n".format(str(self.run_usrp), str(self.run_controller), str(self.run_converter), str(self.run_plotter)))
            print("Running USRP...\n")
            usrp_proc = subprocess.Popen(self.usrp_control_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #outs, errs = usrp_proc.communicate()

            print("Running SGControl...\n")
            controller_proc = subprocess.Popen(self.sg_controller_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #outs, errs = controller_proc.communicate()
            while controller_proc.poll() is None:
                continue
            print("Done sensing medium\n")

            print("Running converter tool...\n")
            converter_proc = subprocess.Popen(self.matlab_converter_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #outs, errs = converter_proc.communicate()
            #proc.wait()
            while converter_proc.poll() is None:
                continue
            print("Done conversion\n")

            print("Running plotter...\n")
            plotter_proc = subprocess.Popen(self.matlab_plotter_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            while plotter_proc.poll() is None:
                continue
            print("Done plotting\n")
            #outs, errs = plotter_proc.communicate()

        # USRP, SGControl, Converter
        elif self.run_usrp and self.run_controller and self.run_converter:
            print("{0} {1} {2} {3}\n".format(str(self.run_usrp), str(self.run_controller), str(self.run_converter), str(self.run_plotter)))
            usrp_proc = subprocess.Popen(self.usrp_control_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)

            controller_proc = subprocess.Popen(self.sg_controller_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #controller_proc.communicate()

            converter_proc = subprocess.Popen(self.matlab_converter_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #outs, errs = converter_proc.communicate()

        # Controller, Converter, Plotter
        elif self.run_controller and self.run_converter and self.run_plotter:
            print("{0} {1} {2} {3}\n".format(str(self.run_usrp), str(self.run_controller), str(self.run_converter), str(self.run_plotter)))
            controller_proc = subprocess.Popen(self.sg_controller_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #outs, errs = controller_proc.communicate()

            converter_proc = subprocess.Popen(self.matlab_converter_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #outs, errs = converter_proc.communicate()
            #proc.wait()

            plotter_proc = subprocess.Popen(self.matlab_plotter_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #outs, errs = plotter_proc.communicate()

        # USRP, Converter, Plotter
        elif self.run_usrp and self.run_converter and self.run_plotter:
            print("{0} {1} {2} {3}\n".format(str(self.run_usrp), str(self.run_controller), str(self.run_converter), str(self.run_plotter)))
            usrp_proc = subprocess.Popen(self.usrp_control_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #outs, errs = usrp_proc.communicate()

            converter_proc = subprocess.Popen(self.matlab_converter_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #outs, errs = converter_proc.communicate()
            #proc.wait()

            plotter_proc = subprocess.Popen(self.matlab_plotter_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #outs, errs = plotter_proc.communicate()

        # USRP, SGControl
        elif self.run_usrp and self.run_controller:
            print("{0} {1} {2} {3}\n".format(str(self.run_usrp), str(self.run_controller), str(self.run_converter), str(self.run_plotter)))
            usrp_proc = subprocess.Popen(self.usrp_control_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #outs, errs = proc.communicate()

            controller_proc = subprocess.Popen(self.sg_controller_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            controller_proc.communicate()
            #outs, errs = proc.communicate()

        # USRP only
        elif self.run_usrp:
            print("{0} {1} {2} {3}\n".format(str(self.run_usrp), str(self.run_controller), str(self.run_converter), str(self.run_plotter)))
            usrp_proc = subprocess.Popen(self.usrp_control_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #outs, errs = usrp_proc.communicate()

        # SGControl only
        elif self.run_controller:
            print("{0} {1} {2} {3}\n".format(str(self.run_usrp), str(self.run_controller), str(self.run_converter), str(self.run_plotter)))
            controller_proc = subprocess.Popen(self.sg_controller_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #outs, errs = controller_proc.communicate()

        # Converter and Plotter
        elif self.run_converter and self.run_plotter:
            print("{0} {1} {2} {3}\n".format(str(self.run_usrp), str(self.run_controller), str(self.run_converter), str(self.run_plotter)))
            converter_proc = subprocess.Popen(self.matlab_converter_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #outs, errs = converter_proc.communicate()
            #proc.wait()

            plotter_proc = subprocess.Popen(self.matlab_plotter_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #outs, errs = plotter_proc.communicate()

        # Converter only
        elif self.run_converter:
            print("{0} {1} {2} {3}\n".format(str(self.run_usrp), str(self.run_controller), str(self.run_converter), str(self.run_plotter)))
            converter_proc = subprocess.Popen(self.matlab_converter_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #outs, errs = converter_proc.communicate()

        # Plotter only
        elif self.run_plotter:
            print("{0} {1} {2} {3}\n".format(str(self.run_usrp), str(self.run_controller), str(self.run_converter), str(self.run_plotter)))
            plotter_proc = subprocess.Popen(self.matlab_plotter_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=None, shell=False)
            #outs, errs = plotter_proc.communicate()

        # What did you select?
        else:
            print("No options or bad options given\n")
            print("{0} {1} {2} {3}\n".format(str(self.run_usrp), str(self.run_controller), str(self.run_converter), str(self.run_plotter)))


    def controller_button_clicked(self):
        sender = self.sender()
        print("Controller button pressed\n")

    def test_button_clicked(self):
        sender = self.sender()
        print("Test button pressed\n")

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
