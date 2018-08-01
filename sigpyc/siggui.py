#!/usr/bin/python3

from PyQt5.QtWidgets import QWidget, QCheckBox, QApplication, QComboBox, QMessageBox, QPushButton, QMainWindow, QLineEdit, QSlider, QLabel
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator

class SiGPyC_GUI(QMainWindow):

    def __init__(self, sigpyc_controller):
        super().__init__()

        # Class variables that are set by toggling the checkboxes. Used to
        # determine which tools to run when the "Run" button is pressed
        self.usrp_state = False
        self.controller_state = False
        self.converter_state = False
        self.plotter_state = False
        self.iperf_client_state = False
        self.iperf_server_state = False

        # Ensure that a proper IP format is used. Taken from
        # https://evileg.com/en/post/57/
        self.ip_range = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        self.ip_regex = QRegExp("^" + self.ip_range + "\\." + self.ip_range + "\\." + self.ip_range + "\\." + self.ip_range + "$")
        self.ip_validator = QRegExpValidator(self.ip_regex, self)

        # Used to pass mode to the controller object
        self.sim_mode = False

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
        self.usrp_checkbox.setToolTip("Sense traffic on the wireless medium")

        # The checkbox for enabling the signal generator, if used
        self.controller_checkbox = QCheckBox('SGControl', self)
        self.controller_checkbox.move(20, 80)
        self.controller_checkbox.stateChanged.connect(self.controller_check)
        self.controller_checkbox.setToolTip("Use the signal generator to add interference (instead of iperf)")

        # The checkbox for the conversion tool
        self.converter_checkbox = QCheckBox('Convert', self)
        self.converter_checkbox.move(20, 140)
        self.converter_checkbox.stateChanged.connect(self.converter_check)
        self.converter_checkbox.setToolTip("Convert the output file created by the USRP")

        # The checkbox for the plotting tool
        self.plotter_checkbox = QCheckBox('Plot', self)
        self.plotter_checkbox.move(20, 200)
        self.plotter_checkbox.stateChanged.connect(self.plotter_check)
        self.plotter_checkbox.setToolTip("Plot the WiFi traffic collected by the Converter tool")

        # The checkbox for running the iperf client
        self.iperf_client_checkbox = QCheckBox('iperf client', self)
        self.iperf_client_checkbox.move(20, 360)
        self.iperf_client_checkbox.stateChanged.connect(self.iperf_client_check)
        self.iperf_client_checkbox.setToolTip("Use iperf to generate wireless transmission data (instead of signal generator)")

        # The checkbox for running iperf server
        self.iperf_server_checkbox = QCheckBox('iperf server', self)
        self.iperf_server_checkbox.move(20, 260)
        self.iperf_server_checkbox.stateChanged.connect(self.iperf_server_check)
        self.iperf_server_checkbox.setToolTip("Provide an iperf server for corresponding client traffic")

        # The checkbox for toggling the run mode (sim or actual)
        self.sim_mode_checkbox = QCheckBox('Simulate', self)
        self.sim_mode_checkbox.move(380, 165)
        self.sim_mode_checkbox.stateChanged.connect(self.sim_mode_check)
        self.sim_mode_checkbox.setToolTip("Run dummy scripts instead of using devices")
        #self.sim_mode_checkbox_text = "Simulate"
        #self.sim_mode_checkbox_label = QLabel(self.sim_mode_checkbox_text, self)
        #self.sim_mode_checkbox_label.move(440, 125)

        # Labels for the iperf IP address boxes
        self.iperf_client_label = QLabel("Client IP", self)
        self.iperf_client_label.move(20, 385)
        self.iperf_server_label = QLabel("Server IP", self)
        self.iperf_server_label.move(20, 285)

        # Create text boxes that use the regex rules and ip_validator from
        # above to ensure that proper IP addresses for the devices are given
        self.iperf_client_lineedit = QLineEdit(self)
        self.iperf_client_lineedit.setValidator(self.ip_validator)
        self.iperf_client_lineedit.textChanged[str].connect(self.on_client_ip)
        self.iperf_client_lineedit.move(20, 410)
        self.iperf_server_lineedit = QLineEdit(self)
        self.iperf_server_lineedit.setValidator(self.ip_validator)
        self.iperf_server_lineedit.textChanged[str].connect(self.on_server_ip)
        self.iperf_server_lineedit.move(20, 310)

        # Configurable fields for the iperf server

        # Create a text box to take the filename used by the USRP and converter
        # tools
        self.file_name_lineedit = QLineEdit(self)
        self.file_name_lineedit.textChanged[str].connect(self.on_name_change)
        self.file_name_lineedit.move(380, 125)
        self.file_name_lineedit.setToolTip("The filename for the USRP to output the data to")
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
        self.runtime_slider.setToolTip("Sense/injection duration for the USRP and signal generator")
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
        self.setWindowTitle('SiGPyC Control Panel')
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

    # Changes the iperf client run state when the checkbox is clicked
    def iperf_client_check(self, state):

        if state == Qt.Checked:
            self.iperf_client_state = True
        else:
            self.iperf_client_state = False

    # Changes the iperf server run state when the checkbox is clicked
    def iperf_server_check(self, state):

        if state == Qt.Checked:
            self.iperf_server_state = True
        else:
            self.iperf_server_state = False

    # Dictates whether or not the test scripts or the target programs are used
    def sim_mode_check(self, state):

        if state == Qt.Checked:
            self.sim_mode = True
        else:
            self.sim_mode = False

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
    def run_button_clicked(self):
        sender = self.sender()
        self.statusBar().showMessage('Running...')

        # USRP, iperf, Converter, Plotter
        if (self.usrp_state and self.iperf_server_state and self.converter_state and self.plotter_state and not self.controller_state):

            self.sigpyc_controller.start_usrp_iperf_server(self.sim_mode)
            self.sigpyc_controller.start_converter(self.sim_mode)
            self.sigpyc_controller.start_plotter(self.sim_mode)

        # USRP, SGControl, Converter, Plotter
        elif (self.usrp_state and self.controller_state and self.converter_state and self.plotter_state and not self.iperf_state):

            self.sigpyc_controller.start_usrp_controller(self.sim_mode)
            self.sigpyc_controller.start_converter(self.sim_mode)
            self.sigpyc_controller.start_plotter(self.sim_mode)

        # USRP, SGControl, Converter
        elif (self.usrp_state and self.controller_state and self.converter_state and not self.plotter_state and not self.iperf_state):

            self.sigpyc_controller.start_usrp_controller(self.sim_mode)
            self.sigpyc_controller.start_converter(self.sim_mode)

        # USRP, iperf, Converter
        elif (self.usrp_state and self.iperf_server_state and self.converter_state and not self.plotter_state and not self.controller_state):

            self.sigpyc_controller.start_usrp_iperf_server(self.sim_mode)
            self.sigpyc_controller.start_converter(self.sim_mode)

        # USRP, Converter, Plotter
        elif (self.usrp_state and self.converter_state and self.plotter_state and not self.controller_state and not self.iperf_state):

            self.sigpyc_controller.start_usrp(self.sim_mode)
            self.sigpyc_controller.start_converter(self.sim_mode)
            self.sigpyc_controller.start_plotter(self.sim_mode)

        # USRP, SGControl
        elif (self.usrp_state and self.controller_state and not self.converter_state and not self.plotter_state):

            self.sigpyc_controller.start_usrp_controller(self.sim_mode)

        # USRP, iperf
        elif (self.usrp_state and self.iperf_server_state and not self.converter_state and not self.plotter_state and not self.controller_state):

            self.sigpyc_controller.start_usrp_iperf_server(self.sim_mode)

        # USRP only
        elif (self.usrp_state and not self.controller_state and not self.converter_state and not self.plotter_state and not self.iperf_state):

            self.sigpyc_controller.start_usrp(self.sim_mode)

        # SGControl only
        elif (self.controller_state and not self.usrp_state and not self.converter_state and not self.plotter_state and not self.iperf_state):

            self.sigpyc_controller.start_controller(self.sim_mode)

        elif (self.usrp_state and self.converter_state and not self.plotter_state and not self.controller_state and not self.iperf_state):

            self.sigpyc_controller.start_usrp(self.sim_mode)
            self.sigpyc_controller.start_converter(self.sim_mode)

        # Converter and Plotter
        elif (self.converter_state and self.plotter_state and not self.usrp_state and not self.controller_state and not self.iperf_state):

            self.sigpyc_controller.start_converter(self.sim_mode)
            self.sigpyc_controller.start_plotter(self.sim_mode)

        # Converter only
        elif (self.converter_state and not self.usrp_state and not self.plotter_state and not self.controller_state and not self.iperf_state):

            self.sigpyc_controller.start_converter(self.sim_mode)

        # Plotter only
        elif (self.plotter_state and not self.converter_state and not self.usrp_state and not self.controller_state and not self.iperf_server_state):

            self.sigpyc_controller.start_plotter(self.sim_mode)

        # iperf only
        elif (self.iperf_server_state and not self.converter_state and not self.usrp_state and not self.controller_state and not self.plotter_state):

            self.sigpyc_controller.start_iperf(self.sim_mode)

        # What did you select?
        else:
            print("No options or bad options given\n")

        print("\nDone sequence\n")

        self.statusBar().showMessage('Idle')
