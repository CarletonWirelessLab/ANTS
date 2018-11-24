#!/usr/bin/python3
from PyQt5.QtWidgets import QWidget, QDialog, QMenuBar, QCheckBox, QAction, QApplication, QComboBox, QMessageBox, QPushButton, QMainWindow, QLineEdit, QSlider, QLabel, QGridLayout, QHBoxLayout, QVBoxLayout, QRadioButton
from PyQt5.QtCore import Qt, QRegExp, QSettings
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> Fixed imports
=======
>>>>>>> 907d2907b91ee68052d3ab35f4651ea3c3ca0487
from PyQt5.QtGui import QRegExpValidator
import sys

class Advanced_GUI(QMainWindow):

    def __init__(self, ants_controller):
        super().__init__()

        # Class variables that are set by toggling the checkboxes. Used to
        # determine which tools to run when the "Run" button is pressed
        self.usrp_state = False
        self.siggen_state = False
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

        # The ANTS Controller object
        self.ants_controller = ants_controller

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
        self.siggen_checkbox = QCheckBox('SGControl', self)
        self.siggen_checkbox.move(20, 80)
        self.siggen_checkbox.stateChanged.connect(self.siggen_check)
        self.siggen_checkbox.setToolTip("Use the signal generator to add interference (instead of iperf)")

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

        # Buttons for access category
        self.ac_voice_button = QRadioButton(self)
        self.ac_video_button = QRadioButton(self)
        self.ac_besteffort_button = QRadioButton(self)
        self.ac_background_button = QRadioButton(self)
        self.ac_voice_button.move(380, 240)
        self.ac_video_button.move(380, 300)
        self.ac_besteffort_button.move(380, 360)
        self.ac_background_button.move(380, 420)
        self.ac_voice_button.setChecked(True)
        self.ac_voice_label = QLabel("Voice", self)
        self.ac_voice_label.move(400, 240)
        self.ac_video_label = QLabel("Video", self)
        self.ac_video_label.move(400, 300)
        self.ac_besteffort_label = QLabel("Best Effort", self)
        self.ac_besteffort_label.move(400, 360)
        self.ac_background_label = QLabel("Background", self)
        self.ac_background_label.move(400, 420)

        self.ac_voice_button.clicked.connect(self.on_ac_voice_clicked)
        self.ac_video_button.clicked.connect(self.on_ac_video_clicked)
        self.ac_besteffort_button.clicked.connect(self.on_ac_besteffort_clicked)
        self.ac_background_button.clicked.connect(self.on_ac_background_clicked)





        self.usrp_settings_menu = USRP_Settings(self)
        self.siggen_settings_menu = SigGen_Settings(self)
        self.plotting_settings_menu = Plotting_Settings(self)
        self.iperf_settings_menu = Iperf_Settings(self)
        self.about_ants_menu = About_ANTS_Menu(self)
        self.license_menu = License_Menu(self)
        #self.usrp_settings_button = QPushButton("USRP Settings", self)
        #self.usrp_settings_button.move(380,220)
        #self.usrp_settings_button.clicked.connect(self.on_usrp_settings_clicked)

        # Create the master menu bar
        self.menubar = self.menuBar()

        self.file_menu = self.menubar.addMenu('File')
        self.sim_state_action = QAction('Simulate', self, checkable=True)
        self.file_menu.addAction(self.sim_state_action)

<<<<<<< HEAD
        self.file_save_action = QAction('Save Profile', self, checkable=True)
        self.file_menu.addAction(self.file_save_action)

        self.file_load_action = QAction('Load Profile', self, checkable=True)
        self.file_menu.addAction(self.file_load_action)

        self.file_reset_action = QAction('Reset Profile', self, checkable=True)
        self.file_menu.addAction(self.file_reset_action)

        self.file_setdefault_action = QAction('Set Profile to Default', self, checkable=True)
=======
        self.file_save_action = QAction('Save Profile', self, checkable=False)
        self.file_menu.addAction(self.file_save_action)

        self.file_load_action = QAction('Load Profile', self, checkable=False)
        self.file_menu.addAction(self.file_load_action)

        self.file_reset_action = QAction('Reset Profile', self, checkable=False)
        self.file_menu.addAction(self.file_reset_action)

        self.file_setdefault_action = QAction('Set Profile to Default', self, checkable=False)
>>>>>>> 907d2907b91ee68052d3ab35f4651ea3c3ca0487
        self.file_menu.addAction(self.file_setdefault_action)

        # Add a checkbox to toggle the USRP to the USRP menu
        self.usrp_settings = self.menubar.addMenu('USRP')
        self.usrp_state_action = QAction('Enable', self, checkable=True)
        self.usrp_state_action.triggered.connect(self.usrp_check)
        self.usrp_settings.addAction(self.usrp_state_action)

        # Add a settings button to the USRP menu
        self.usrp_settings_action = QAction('Settings', self, checkable=False)
        self.usrp_settings_action.triggered.connect(self.on_usrp_settings_clicked)
        self.usrp_settings.addAction(self.usrp_settings_action)

        # Add a checkbox to toggle the signal generator to its menu
        self.siggen_settings = self.menubar.addMenu('Signal Generator')

        self.siggen_state_action = QAction('Enable', self, checkable=True)
        self.siggen_state_action.triggered.connect(self.siggen_check)
        self.siggen_settings.addAction(self.siggen_state_action)

        self.siggen_settings_action = QAction('Settings', self, checkable=False)
        self.siggen_settings_action.triggered.connect(self.on_siggen_settings_clicked)
        self.siggen_settings.addAction(self.siggen_settings_action)

        # Add checkboxes for the plotter and converter to the plotting menu
        self.plotting_settings = self.menubar.addMenu('Convert/Plot')

        self.converter_state_action = QAction('Enable Converter', self, checkable=True)
        self.converter_state_action.triggered.connect(self.converter_check)
        self.plotting_settings.addAction(self.converter_state_action)
        self.plotter_state_action = QAction('Enable Plotter', self, checkable=True)
        self.plotter_state_action.triggered.connect(self.plotter_check)
        self.plotting_settings.addAction(self.plotter_state_action)

        self.plotting_settings_action = QAction('Settings', self, checkable=False)
        self.plotting_settings_action.triggered.connect(self.on_plotting_settings_clicked)
        self.plotting_settings.addAction(self.plotting_settings_action)

        self.iperf_menu = self.menubar.addMenu('iperf')

        self.iperf_client_state_action = QAction('Enable Client', self, checkable=True)
        self.iperf_client_state_action.triggered.connect(self.iperf_client_check)
        self.iperf_menu.addAction(self.iperf_client_state_action)
        self.iperf_server_state_action = QAction('Enable Server', self, checkable=True)
        self.iperf_server_state_action.triggered.connect(self.iperf_server_check)
        self.iperf_menu.addAction(self.iperf_server_state_action)

        self.iperf_settings_action = QAction('Settings', self, checkable=False)
        self.iperf_settings_action.triggered.connect(self.on_iperf_settings_clicked)
        self.iperf_menu.addAction(self.iperf_settings_action)

        self.about_menu = self.menubar.addMenu('About')

        self.about_ants_action = QAction('About ants', self, checkable=False)
        self.about_ants_action.triggered.connect(self.on_about_ants_menu_clicked)
        self.about_menu.addAction(self.about_ants_action)

        self.about_license_action = QAction('Licensing Information', self, checkable=False)
        self.about_license_action.triggered.connect(self.on_license_menu_clicked)
        self.about_menu.addAction(self.about_license_action)

        # The button for running the entire sequence
        self.run_btn = QPushButton('Run', self)
        self.run_btn.setToolTip('Run the test sequences selected')
        self.run_btn.resize(self.run_btn.sizeHint())
        self.run_btn.move(380, 20)
        self.run_btn.clicked.connect(self.run_button_clicked)

        # Set up the GUI window
        self.setGeometry(300, 600, 500, 500)
        self.setWindowTitle('ANTS Control Panel')
        self.show()

        #--------Save Checkbox values on the main window here----------

        # get settings checkbox values from main window
        checkboxSettings = QSettings()
        check_USRP_checkbox = checkboxSettings.value('usrp_checkbox',False,type=bool)
        check_SGControl_checkbox = checkboxSettings.value('siggen_checkbox',False,type=bool)
        check_Convert_checkbox = checkboxSettings.value('converter_checkbox',False,type=bool)
        check_Plot_checkbox = checkboxSettings.value('plotter_checkbox',False,type=bool)
        check_iperf_client_checkbox = checkboxSettings.value('iperf_client_checkbox',False,type=bool)
        check_iperf_server_checkbox = checkboxSettings.value('iperf_server_checkbox',False,type=bool)
        check_Simulate_checkbox = checkboxSettings.value('sim_mode_checkbox',False,type=bool)

        # set state
        self.usrp_checkbox.setChecked(check_USRP_checkbox)
        self.siggen_checkbox.setChecked(check_SGControl_checkbox)
        self.converter_checkbox.setChecked(check_Convert_checkbox)
        self.plotter_checkbox.setChecked(check_Plot_checkbox)
        self.iperf_client_checkbox.setChecked(check_iperf_client_checkbox)
        self.iperf_server_checkbox.setChecked(check_iperf_server_checkbox)
        self.sim_mode_checkbox.setChecked(check_Simulate_checkbox)

        # connect the slot to the signal by clicking the checkbox to save the state settings
        self.usrp_checkbox.clicked.connect(self.save_usrp_checkbox_settings)
        self.siggen_checkbox.clicked.connect(self.save_siggen_checkbox_settings)
        self.converter_checkbox.clicked.connect(self.save_converter_checkbox_settings)
        self.plotter_checkbox.clicked.connect(self.save_plotter_checkbox_settings)
        self.iperf_client_checkbox.clicked.connect(self.save_iperf_client_checkbox_settings)
        self.iperf_server_checkbox.clicked.connect(self.save_iperf_server_checkbox_settings)
        self.sim_mode_checkbox.clicked.connect(self.save_sim_mode_checkbox_settings)

    def save_usrp_checkbox_settings(self):
        settings = QSettings()
        settings.setValue('usrp_checkbox', self.usrp_checkbox.isChecked())
        settings.sync()

    def save_siggen_checkbox_settings(self):
        settings = QSettings()
        settings.setValue('siggen_checkbox', self.siggen_checkbox.isChecked())
        settings.sync()

    def save_converter_checkbox_settings(self):
        settings = QSettings()
        settings.setValue('converter_checkbox', self.converter_checkbox.isChecked())
        settings.sync()

    def save_plotter_checkbox_settings(self):
        settings = QSettings()
        settings.setValue('plotter_checkbox', self.plotter_checkbox.isChecked())
        settings.sync()

    def save_iperf_client_checkbox_settings(self):
        settings = QSettings()
        settings.setValue('iperf_client_checkbox', self.iperf_client_checkbox.isChecked())
        settings.sync()

    def save_iperf_server_checkbox_settings(self):
        settings = QSettings()
        settings.setValue('iperf_server_checkbox', self.iperf_server_checkbox.isChecked())
        settings.sync()

    def save_sim_mode_checkbox_settings(self):
        settings = QSettings()
        settings.setValue('sim_mode_checkbox', self.sim_mode_checkbox.isChecked())
        settings.sync()
    #--------end of save checkbox---------

    def on_usrp_settings_clicked(self):
        self.usrp_settings_menu.show()

    def on_siggen_settings_clicked(self):
        self.siggen_settings_menu.show()

    def on_plotting_settings_clicked(self):
        self.plotting_settings_menu.show()

    def on_iperf_settings_clicked(self):
        self.iperf_settings_menu.show()

    def on_about_ants_menu_clicked(self):
        self.about_ants_menu.show()

    def on_license_menu_clicked(self):
        self.license_menu.show()

    # Action functions for access category radio buttons

    def on_ac_voice_clicked(self):
        self.ants_controller.access_category = 0

    def on_ac_video_clicked(self):
        self.ants_controller.access_category = 1

    def on_ac_besteffort_clicked(self):
        self.ants_controller.access_category = 2

    def on_ac_background_clicked(self):
        self.ants_controller.access_category = 3

    # Changes the usrp run state when the checkbox is clicked
    def usrp_check(self, state):

        if state:
            self.usrp_state = True
        else:
            self.usrp_state = False

    # Changes the signal generator run state when the checkbox is clicked
    def siggen_check(self, state):

        if state:
            self.siggen_state = True
        else:
            self.siggen_state = False

    # Changes the converter run state when the checkbox is clicked
    def converter_check(self, state):

        if state:
            self.converter_state = True
        else:
            self.converter_state = False

    # Changes the plotter run state when the checkbox is clicked
    def plotter_check(self, state):

        if state:
            self.plotter_state = True
        else:
            self.plotter_state = False

    # Changes the iperf client run state when the checkbox is clicked
    def iperf_client_check(self, state):

        if state:
            self.iperf_client_state = True
        else:
            self.iperf_client_state = False

    # Changes the iperf server run state when the checkbox is clicked
    def iperf_server_check(self, state):

        if state:
            self.iperf_server_state = True
        else:
            self.iperf_server_state = False

    # Dictates whether or not the test scripts or the target programs are used
    def sim_mode_check(self, state):

        if state:
            self.sim_mode = True
        else:
            self.sim_mode = False

    # Controls changing the value pointed to by the slider. The slider should
    # allow ranges between 0.5 and 10, but since the class only supports
    # integers, some math must be done to the actual value when it is moved
    def change_value(self, value):

        if value == 0:
            self.ants_controller.run_time = 0.5
        elif value == 20:
            self.ants_controller.run_time = 10
        else:
            self.ants_controller.run_time = value / 2.0
        self.runtime_label.setText(str(self.ants_controller.run_time) + " seconds")

    # Checks to make sure iperf_client_addr is set to a realistic IP value
    def on_client_ip(self, text):

        if self.iperf_client_lineedit.hasAcceptableInput():
            self.ants_controller.iperf_client_addr = text

    # Checks to make sure iperf_server_addr is set to a realistic IP value
    def on_server_ip(self, text):

        if self.iperf_server_lineedit.hasAcceptableInput():
            self.ants_controller.iperf_server_addr = text

    # Set file name based on what's in the box
    def on_name_change(self, text):

        self.ants_controller.file_name = text

    def on_iperf_IP_TOS_field_change(self, text):
        pass

    def on_iperf_bandwidth_field_change(self, text):
        pass

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
    # Should make this more modular, turn it into a dictionary with functions
    # as the values or something
    def run_button_clicked(self):
        sender = self.sender()
        self.statusBar().showMessage('Running...')

        # USRP, iperf, Converter, Plotter
        if (self.usrp_state and self.iperf_server_state and self.converter_state and self.plotter_state and not self.siggen_state):

            self.ants_controller.start_usrp_iperf_server(self.sim_mode)
            self.ants_controller.start_converter(self.sim_mode)
            self.ants_controller.start_plotter(self.sim_mode)

        # USRP, SGControl, Converter, Plotter
        elif (self.usrp_state and self.siggen_state and self.converter_state and self.plotter_state and not self.iperf_server_state):

            self.ants_controller.start_usrp_controller(self.sim_mode)
            self.ants_controller.start_converter(self.sim_mode)
            self.ants_controller.start_plotter(self.sim_mode)

        # USRP, SGControl, Converter
        elif (self.usrp_state and self.siggen_state and self.converter_state and not self.plotter_state and not self.iperf_server_state):

            self.ants_controller.start_usrp_controller(self.sim_mode)
            self.ants_controller.start_converter(self.sim_mode)

        # USRP, iperf, Converter
        elif (self.usrp_state and self.iperf_server_state and self.converter_state and not self.plotter_state and not self.siggen_state):

            self.ants_controller.start_usrp_iperf_server(self.sim_mode)
            self.ants_controller.start_converter(self.sim_mode)

        # USRP, Converter, Plotter
        elif (self.usrp_state and self.converter_state and self.plotter_state and not self.siggen_state and not self.iperf_server_state):

            self.ants_controller.start_usrp(self.sim_mode)
            self.ants_controller.start_converter(self.sim_mode)
            self.ants_controller.start_plotter(self.sim_mode)

        # USRP, SGControl
        elif (self.usrp_state and self.siggen_state and not self.converter_state and not self.plotter_state and not self.iperf_server_state):

            self.ants_controller.start_usrp_controller(self.sim_mode)

        # USRP, iperf
        elif (self.usrp_state and self.iperf_server_state and not self.converter_state and not self.plotter_state and not self.siggen_state):

            self.ants_controller.start_usrp_iperf_server(self.sim_mode)

        # USRP only
        elif (self.usrp_state and not self.siggen_state and not self.converter_state and not self.plotter_state and not self.iperf_server_state):

            self.ants_controller.start_usrp(self.sim_mode)

        # SGControl only
        elif (self.siggen_state and not self.usrp_state and not self.converter_state and not self.plotter_state and not self.iperf_server_state):

            self.ants_controller.start_controller(self.sim_mode)

        elif (self.usrp_state and self.converter_state and not self.plotter_state and not self.siggen_state and not self.iperf_server_state):

            self.ants_controller.start_usrp(self.sim_mode)
            self.ants_controller.start_converter(self.sim_mode)

        # Converter and Plotter
        elif (self.converter_state and self.plotter_state and not self.usrp_state and not self.siggen_state and not self.iperf_server_state):

            self.ants_controller.start_converter(self.sim_mode)
            self.ants_controller.start_plotter(self.sim_mode)

        # Converter only
        elif (self.converter_state and not self.usrp_state and not self.plotter_state and not self.siggen_state and not self.iperf_server_state):

            self.ants_controller.start_converter(self.sim_mode)

        # Plotter only
        elif (self.plotter_state and not self.converter_state and not self.usrp_state and not self.siggen_state and not self.iperf_server_state):

            self.ants_controller.start_plotter(self.sim_mode)

        # iperf only
        elif (self.iperf_server_state and not self.converter_state and not self.usrp_state and not self.siggen_state and not self.plotter_state):

            self.ants_controller.start_iperf_server(self.sim_mode)

        # What did you select?
        else:
            print("No options or bad options given\n")

        print("\nDone sequence\n")

        self.statusBar().showMessage('Idle')


class USRP_Settings(QMainWindow):

    def __init__(self, parent):
        super(USRP_Settings, self).__init__(parent)

        self.pushButton = QPushButton("click me")

        self.setCentralWidget(self.pushButton)

class SigGen_Settings(QMainWindow):

    def __init__(self, parent):
        super(SigGen_Settings, self).__init__(parent)

        self.pushButton = QPushButton("click me")

        self.setCentralWidget(self.pushButton)

class Plotting_Settings(QMainWindow):

    def __init__(self, parent):
        super(Plotting_Settings, self).__init__(parent)

        self.pushButton = QPushButton("click me")

        self.setCentralWidget(self.pushButton)

class Iperf_Settings(QDialog):

    def __init__(self, parent):
        super(Iperf_Settings, self).__init__(parent)

        #self.pushButton = QPushButton("click me")
        self.ip_range = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        self.ip_regex = QRegExp("^" + self.ip_range + "\\." + self.ip_range + "\\." + self.ip_range + "\\." + self.ip_range + "$")
        self.ip_validator = QRegExpValidator(self.ip_regex, self)

        self.iperf_client_lineedit = QLineEdit(self)
        self.iperf_client_lineedit.setValidator(self.ip_validator)
        self.iperf_client_lineedit.textChanged[str].connect(parent.on_client_ip)
        #self.iperf_client_lineedit.move(20, 410)
        self.iperf_server_lineedit = QLineEdit(self)
        self.iperf_server_lineedit.setValidator(self.ip_validator)
        self.iperf_server_lineedit.textChanged[str].connect(parent.on_server_ip)

        self.iperf_IP_TOS_field = QLineEdit(self)
        self.iperf_IP_TOS_field.textChanged[str].connect(parent.on_iperf_IP_TOS_field_change)

        self.iperf_bandwidth_field = QLineEdit(self)
        self.iperf_bandwidth_field.textChanged[str].connect(parent.on_iperf_bandwidth_field_change)

        grid = QGridLayout()
        self.setLayout(grid)
        self.setGeometry(300, 300, 450, 225)
        self.setWindowTitle("iperf Settings")

        self.iperf_client_label = QLabel("Client IP", self)
        self.iperf_server_label = QLabel("Server IP", self)
        self.iperf_IP_TOS_label = QLabel("IP TOS", self)
        self.iperf_bandwidth_label = QLabel("Bandwidth", self)

        grid.addWidget(self.iperf_client_label, 0, 0)
        grid.addWidget(self.iperf_server_label, 1, 0)
        grid.addWidget(self.iperf_IP_TOS_label, 2, 0)
        grid.addWidget(self.iperf_bandwidth_label, 3, 0)
        grid.addWidget(self.iperf_client_lineedit, 0, 1)
        grid.addWidget(self.iperf_server_lineedit, 1, 1)
        grid.addWidget(self.iperf_IP_TOS_field, 2, 1)
        grid.addWidget(self.iperf_bandwidth_field, 3, 1)

class About_ANTS_Menu(QMainWindow):

    def __init__(self, parent):
        super(About_ANTS_Menu, self).__init__(parent)

        self.ants_message = QLabel()
        self.ants_message.setText("ANTS (the Automated Networking Test Suite) is an application written \
by Trevor Gamblin (tvgamblin@gmail.com) with the goal of automating and simplifying compliance testing of \
wireless devices. For more information, or if you have suggestions or bugs to report, visit \
https://github.com/threexc/ANTS, or contact the author directly.\n")

        self.ants_message.setMargin(10)
        self.ants_message.setWordWrap(1)
        self.setCentralWidget(self.ants_message)

class License_Menu(QMainWindow):

    def __init__(self, parent):
        super(License_Menu, self).__init__(parent)

        self.license_message = QLabel()
        self.license_message.setText("MIT License\n\
\n\
Copyright (c) 2018 Trevor Gamblin - tvgamblin@gmail.com\n\
\n\
Permission is hereby granted, free of charge, to any person obtaining a copy\n\
of this software and associated documentation files (the \"Software\"), to deal\n\
in the Software without restriction, including without limitation the rights\n\
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell\n\
copies of the Software, and to permit persons to whom the Software is\n\
furnished to do so, subject to the following conditions:\n\
\n\
The above copyright notice and this permission notice shall be included in all\n\
copies or substantial portions of the Software.\n\
\n\
THE SOFTWARE IS PROVIDED \"AS IS\", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\n\
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\n\
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\n\
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\n\
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\n\
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\n\
SOFTWARE.")
        self.license_message.setMargin(10)
        self.setCentralWidget(self.license_message)
