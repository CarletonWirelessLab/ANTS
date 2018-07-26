#!/usr/bin/python3

from PyQt5.QtWidgets import QWidget, QCheckBox, QApplication, QComboBox, QMessageBox, QPushButton, QMainWindow, QLineEdit, QSlider, QLabel
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator

class SiGPyC_GUI(QMainWindow):

    def __init__(self, sigpyc_controller, test_mode=False):
        super().__init__()

        # Class variables that are set by toggling the checkboxes. Used to
        # determine which tools to run when the "Run" button is pressed
        self.usrp_state = False
        self.controller_state = False
        self.converter_state = False
        self.plotter_state = False
        self.iperf_state = False

        # Ensure that a proper IP format is used. Taken from
        # https://evileg.com/en/post/57/
        self.ip_range = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        self.ip_regex = QRegExp("^" + self.ip_range + "\\." + self.ip_range + "\\." + self.ip_range + "\\." + self.ip_range + "$")
        self.ip_validator = QRegExpValidator(self.ip_regex, self)

        # Used to pass mode to the controller object
        self.test_mode = test_mode

        # The SiGPyC Controller object
        self.sigpyc_controller = sigpyc_controller

        # Starts up the UI
        self.init_UI()


    # The primary method for setting up the buttons and other widgets, including
    # the arguments to be run using subprocess.Popen()
    def init_UI(self):

        self.statusBar().showMessage('Idle')

        # The checkbox for enabling the USRP
        self.usrp_checkbox = QCheckBox('USRP', self)
        self.usrp_checkbox.move(20, 20)
        self.usrp_checkbox.stateChanged.connect(self.usrp_check)

        # The checkbox for enabling the signal generator, if used
        self.controller_checkbox = QCheckBox('SGControl', self)
        self.controller_checkbox.move(20, 80)
        self.controller_checkbox.stateChanged.connect(self.controller_check)

        # The checkbox for the conversion tool
        self.converter_checkbox = QCheckBox('Convert', self)
        self.converter_checkbox.move(20, 140)
        self.converter_checkbox.stateChanged.connect(self.converter_check)

        # The checkbox for the plotting tool
        self.plotter_checkbox = QCheckBox('Plot', self)
        self.plotter_checkbox.move(20, 200)
        self.plotter_checkbox.stateChanged.connect(self.plotter_check)

        # The checkbox for running iperf
        self.iperf_checkbox = QCheckBox('iperf', self)
        self.iperf_checkbox.move(20, 260)
        self.iperf_checkbox.stateChanged.connect(self.iperf_check)

        # Labels for the iperf IP address boxes
        self.iperf_client_label = QLabel("Client IP", self)
        self.iperf_client_label.move(20, 300)
        self.iperf_server_label = QLabel("Server IP", self)
        self.iperf_server_label.move(20, 360)

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
            self.sigpyc_controller.run_time = 0.5
        elif value == 20:
            self.sigpyc_controller.run_time = 10
        else:
            self.sigpyc_controller.run_time = value / 2.0
        self.runtime_label.setText(str(self.sigpyc_controller.run_time) + " seconds")

    # Checks to make sure iperf_client_addr is set to a realistic IP value
    def on_client_ip(self, text):

        if self.iperf_client_lineedit.hasAcceptableInput():
            self.sigpyc_controller.iperf_client_addr = text

    # Checks to make sure iperf_server_addr is set to a realistic IP value
    def on_server_ip(self, text):

        if self.iperf_server_lineedit.hasAcceptableInput():
            self.sigpyc_controller.iperf_server_addr = text

    # Set file name based on what's in the box
    def on_name_change(self, text):

        self.sigpyc_controller.file_name = text

    # Make sure we get prompted before closing the GUI
    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
            "Are you sure you want to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    # The logic for when the "Run" button is pressed. It checks to see which
    # boxes are checked, then runs based on what it sees. Is there a case where
    # we don't want to run the USRP? Should make this more modular, turn it
    # into a dictionary with functions as the values
    def run_button_clicked(self, options):
        sender = self.sender()
        self.statusBar().showMessage('Running...')

        # USRP, iperf, Converter, Plotter
        if (self.usrp_state and self.iperf_state and self.converter_state and self.plotter_state and not self.controller_state):

            self.sigpyc_controller.start_usrp_iperf()
            self.sigpyc_controller.start_converter()
            self.sigpyc_controller.start_plotter()

        # USRP, SGControl, Converter, Plotter
        elif (self.usrp_state and self.controller_state and self.converter_state and self.plotter_state and not self.iperf_state):

            self.sigpyc_controller.start_usrp_controller()
            self.sigpyc_controller.start_converter()
            self.sigpyc_controller.start_plotter()

        # USRP, SGControl, Converter
        elif (self.usrp_state and self.controller_state and self.converter_state and not self.plotter_state and not self.iperf_state):

            self.sigpyc_controller.start_usrp_controller()
            self.sigpyc_controller.start_converter()

        # USRP, iperf, Converter
        elif (self.usrp_state and self.iperf_state and self.converter_state and not self.plotter_state and not self.controller_state):

            self.sigpyc_controller.start_usrp_iperf()
            self.sigpyc_controller.start_converter()

        # USRP, Converter, Plotter
        elif (self.usrp_state and self.converter_state and self.plotter_state and not self.controller_state and not self.iperf_state):

            self.sigpyc_controller.start_usrp()
            self.sigpyc_controller.start_converter()
            self.sigpyc_controller.start_plotter()

        # USRP, SGControl
        elif (self.usrp_state and self.controller_state and not self.converter_state and not self.plotter_state):

            self.sigpyc_controller.start_usrp_controller()

        # USRP, iperf
        elif (self.usrp_state and self.iperf_state and not self.converter_state and not self.plotter_state and not self.controller_state):

            self.sigpyc_controller.start_usrp_iperf()

        # USRP only
        elif (self.usrp_state and not self.controller_state and not self.converter_state and not self.plotter_state and not self.iperf_state):

            self.sigpyc_controller.start_usrp()

        # SGControl only
        elif (self.controller_state and not self.usrp_state and not self.converter_state and not self.plotter_state and not self.iperf_state):

            self.sigpyc_controller.start_controller()

        elif (self.usrp_state and self.converter_state and not self.plotter_state and not self.controller_state and not self.iperf_state):

            self.sigpyc_controller.start_usrp()
            self.sigpyc_controller.start_converter()

        # Converter and Plotter
        elif (self.converter_state and self.plotter_state and not self.usrp_state and not self.controller_state and not self.iperf_state):

            self.sigpyc_controller.start_converter()
            self.sigpyc_controller.start_plotter()

        # Converter only
        elif (self.converter_state and not self.usrp_state and not self.plotter_state and not self.controller_state and not self.iperf_state):

            self.sigpyc_controller.start_converter()

        # Plotter only
        elif (self.plotter_state and not self.converter_state and not self.usrp_state and not self.controller_state and not self.iperf_state):

            self.sigpyc_controller.start_plotter()

        # iperf only
        elif (self.iperf_state and not self.converter_state and not self.usrp_state and not self.controller_state and not self.plotter_state):

            self.sigpyc_controller.start_iperf()

        # What did you select?
        else:
            print("No options or bad options given\n")

        self.statusBar().showMessage('Idle')
