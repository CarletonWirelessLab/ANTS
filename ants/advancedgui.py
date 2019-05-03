#!/usr/bin/python3

import math
from PyQt5.QtWidgets import QWidget, QDialog, QMenuBar, QCheckBox, QAction
from PyQt5.QtWidgets import QApplication, QComboBox, QMessageBox, QPushButton
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QSlider, QLabel, QGridLayout
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QRadioButton, QTabWidget
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtCore import Qt, QRegExp, QSettings, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import *
from network_scan import *
from interfaces_scan import *
from subprocess import *
from textwrap import dedent


class Overlay(QWidget):

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        palette = QPalette(self.palette())
        palette.setColor(palette.Background, Qt.transparent)
        self.setPalette(palette)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), QBrush(QColor(255,255,255,127)))
        painter.setPen(QPen(Qt.NoPen))

        for i in range(6):
            if (self.counter / 5) %6 == i:
                painter.setBrush(QBrush(QColor(127 + (self.counter % 5)*32, 127, 127)))
            else:
                painter.setBrush(QBrush(QColor(127, 127, 127)))
                painter.drawEllipse(
                self.width()/2 + 30 * math.cos(2 * math.pi * i / 6.0) - 10,
                self.height()/2 + 30 * math.sin(2 * math.pi * i / 6.0) - 10, 20, 20) 

        painter.end()

    def showEvent(self, event):
        self.timer = self.startTimer(50)
        self.counter = 0 
        event.accept()

    def hideEvent(self, event):
        self.killTimer(self.timer)
        event.accept()

    def timerEvent(self, event):     
        self.counter += 1
        self.update()

# The parent "table" class that holds all of the functional tabs
class ANTS_Table(QWidget):

    def __init__(self, main_gui, ants_controller, showOverlay, hideOverlay):
        super(QWidget, self).__init__(main_gui)

        # Initialize the ANTS controller object to run the tests
        self.ants_controller = ants_controller

        # Set the layout type for the GUI and instantiate the tabs widget
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        # Instantiate all of the tab objects needed for the GUI
        self.results_tab = ANTS_Results_Tab(self, self.ants_controller)
        self.settings_tab = ANTS_Settings_Tab(self, self.results_tab, self.ants_controller, self.tabs, showOverlay, hideOverlay)
        self.about_tab = ANTS_About_Tab(self, self.ants_controller)
        self.license_tab = ANTS_License_Tab(self, self.ants_controller)
        self.tabs.resize(300, 200)

        self.tabs.addTab(self.settings_tab, "Control Settings")
        self.tabs.addTab(self.results_tab, "Results")
        self.tabs.addTab(self.about_tab, "About")
        self.tabs.addTab(self.license_tab, "License")

        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

class ANTS_Results_Tab(QWidget):

    def __init__(self, tabs_object, ants_controller):
        super(QWidget, self).__init__(tabs_object)
        self.ants_controller = ants_controller
        self.layout = QGridLayout(self)

        # Set up the graphics for the main display
        self.graphic_label = QLabel(self)
        self.graphic_label.setStyleSheet("""
            background-color: grey;
            color: white;
            font: bold;
            padding: 1px;
            border-width: 1px;
            border-style: panel;
            border-radius: 1px;
            border-color: white;
        """)

        self.compliance_label = QLabel("Compliance (%): N/A")
        self.aggression_label = QLabel("Aggression (%): N/A")
        self.submission_label = QLabel("Submission (%): N/A")

        # The blank graphic box where the plots will be painted
        self.layout.addWidget(self.graphic_label, 0, 0, 5, 5)

        # The widgets in the information/run bar on the right side of the GUI

        self.layout.addWidget(self.compliance_label, 3, 6, 1, 1)
        self.layout.addWidget(self.aggression_label, 4, 6, 1, 1)
        self.layout.addWidget(self.submission_label, 5, 6, 1, 1)

        self.layout.setColumnStretch(6, 1)
        self.layout.setRowStretch(4, 1)

        # The following four buttons are specifically for displaying one of the
        # four plot types

        self.bin_button = QPushButton("Show Bin Distribution", self)
        self.bin_button.setToolTip('Show the bin probability and treshold data for the run')
        self.bin_button.resize(self.bin_button.sizeHint())
        self.bin_button.clicked.connect(self.bin_button_clicked)
        self.layout.addWidget(self.bin_button, 6, 0, 1, 1)

        self.interframe_button = QPushButton("Show Interframe Spacing", self)
        self.interframe_button.setToolTip('Show the interframe spacing histogram')
        self.interframe_button.resize(self.interframe_button.sizeHint())
        self.interframe_button.clicked.connect(self.interframe_button_clicked)
        self.layout.addWidget(self.interframe_button, 6, 1, 1, 1)

        self.raw_signal_button = QPushButton("Show Raw Signal Data", self)
        self.raw_signal_button.setToolTip('Show the raw signal Fourier Transform')
        self.raw_signal_button.resize(self.raw_signal_button.sizeHint())
        self.raw_signal_button.clicked.connect(self.raw_signal_button_clicked)
        self.layout.addWidget(self.raw_signal_button, 6, 2, 1, 1)

        self.txop_button = QPushButton("TXOP", self)
        self.txop_button.setToolTip('Show Transmission Opportunity Durations')
        self.txop_button.resize(self.txop_button.sizeHint())
        self.txop_button.clicked.connect(self.txop_button_clicked)
        self.layout.addWidget(self.txop_button, 6, 3, 1, 1)

        self.setLayout(self.layout)

    # When the bin distribution button is clicked, display the bin distribution QPixmap contents
    def bin_button_clicked(self):
        self.bin_pixmap.load(self.bin_pixmap_path)
        self.graphic_label.setPixmap(self.bin_pixmap)

    # When the interframe spacing button is clicked, display the bin distribution QPixmap contents
    def interframe_button_clicked(self):
        self.interframe_pixmap.load(self.interframe_pixmap_path)
        self.graphic_label.setPixmap(self.interframe_pixmap)

    # When the raw signal button is clicked display the raw signal data QPixmap contents
    def raw_signal_button_clicked(self):
        self.raw_signal_pixmap.load(self.raw_signal_pixmap_path)
        self.graphic_label.setPixmap(self.raw_signal_pixmap)

    # When the TXOP button is clicked, display the transmission opportunity distribution QPixmap contents
    def txop_button_clicked(self):
        self.txop_pixmap.load(self.txop_pixmap_path)
        self.graphic_label.setPixmap(self.txop_pixmap)

class ANTS_ControlThread(QThread):
    signal = pyqtSignal()

    def __init__(self, antsController):
        QThread.__init__(self)
        self._antsController = antsController
    
    def __def__(self):
        self.wait()

    def run(self):
        self._antsController.run_n_times()
        self.signal.emit()

# The catch-all tab widget for settings related to ANTS. Data entered here should be passed to the ANTS controller object
class ANTS_Settings_Tab(QWidget):
    def __init__(self, tabs_object, results_tab, ants_controller, ants_table, showOverlay, hideOverlay):
        super(QWidget, self).__init__(tabs_object)
        self.ants_controller = ants_controller
        self.ants_table = ants_table
        self.results_tab = results_tab
        self.showOverlay = showOverlay
        self.hideOverlay = hideOverlay
        # Always run at least once
        self.num_runs = 1

        # Define tab layout and set column structure
        self.layout = QGridLayout(self)
        self.setLayout(self.layout)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 1)
        self.layout.setColumnStretch(2, 1)

        # IP Validator for the IP fields
        self.ip_range = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        self.ip_regex = QRegExp("^" + self.ip_range + "\\." + self.ip_range + "\\." + self.ip_range + "\\." + self.ip_range + "$")
        self.ip_validator = QRegExpValidator(self.ip_regex, self)

        # The button for running the entire sequence
        self.run_btn = QPushButton('Run', self)
        self.run_btn.setToolTip('Run the test sequences selected')
        self.run_btn.resize(self.run_btn.sizeHint())
        self.run_btn.clicked.connect(self.run_button_clicked, 5)

        # The button for scanning the entire sequence
        self.scan_btn = QPushButton('Scan Wi-Fi', self)
        self.scan_btn.setToolTip('Scan the Wi-Fi networks')
        self.scan_btn.resize(self.scan_btn.sizeHint())
        self.scan_btn.clicked.connect(self.scan_button_clicked, 5)

        # The checkbox for confirming that automatic network routing should be performed
        self.routing_checkbox = QCheckBox("Perform Auto Routing", self)
        self.routing_checkbox.toggle()
        self.routing_checkbox.setToolTip("Allow ANTS to perform custom networking setup (requires root permissions). Off by default")
        self.routing_checkbox.stateChanged.connect(self.configure_routing)


        # Create a text box to take the filename used by the USRP and converter
        # tools
        self.file_name_lineedit = QLineEdit(self)
        self.file_name_lineedit.textChanged[str].connect(self.on_name_change)
        self.file_name_lineedit.setToolTip("The filename for the USRP to output the data to")
        self.file_name_text = "Test Name"
        self.file_name_label = QLabel(self.file_name_text, self)

        # Run time slider set up
        self.runtime_slider = QSlider(Qt.Horizontal, self)
        self.runtime_slider.setFocusPolicy(Qt.NoFocus)
        self.runtime_slider.setGeometry(380,70,100,30)
        self.runtime_slider.valueChanged[int].connect(self.change_value)
        self.runtime_slider.setMinimum(0)
        self.runtime_slider.setMaximum(20)
        self.runtime_slider.setTickInterval(1)
        self.runtime_slider.setToolTip("Sense/injection duration for the USRP and signal generator")
        self.runtime_text = "Runtime " + str(0.5) + " seconds"
        self.runtime_label = QLabel(self.runtime_text, self)


        # Text box for specifying the IP address of the access point to be used for testing
        self.network_ap_lineedit = QLineEdit(self)
        self.network_ap_lineedit_label = QLabel("Access Point IP", self)
        self.network_ap_lineedit.setValidator(self.ip_validator)
        self.network_ap_lineedit.setText('192.168.1.1')
        self.ants_controller.iperf_ap_addr = '192.168.1.1'
        self.network_ap_lineedit.textChanged[str].connect(self.on_ap_ip)

        # Text box for specifying the IP address of the access point to be used for testing
        self.center_frequency_lineedit = QLineEdit(self)
        self.center_frequency_lineedit_label = QLabel("Center Frequency (GHz)", self)
        self.center_frequency_lineedit.setText('5.180')
        self.ants_controller.center_frequency = '5.180'
        self.center_frequency_lineedit.textChanged[str].connect(self.on_center_frequency)

        # Specify the iperf type-of-service value (client only)
        self.network_WiFi = QComboBox(self)
        self.network_WiFi_label = QLabel("Wi-Fi Networks", self)
        self.network_WiFi.activated[str].connect(self.on_network_WiFi_change)

        # Specify the itype of the UUT, supervised or supervising
        self.UUT_type = QComboBox(self)
        self.UUT_type_label = QLabel("UUT Type", self)
        self.UUT_type.activated[str].connect(self.on_UUT_type_change)
        self.UUT_type.addItem("Supervising")
        self.UUT_type.addItem("Supervised")
        self.ants_controller.UUT_type = "Supervising"
        print("UUT TYPE IS: SUPERVISING")

        # Set the iperf bandwidth value (client only)
        self.network_bandwidth_slider_label = QLabel(None, self)
        self.network_bandwidth_slider = QSlider(Qt.Horizontal, self)
        self.network_bandwidth_slider.setFocusPolicy(Qt.NoFocus)
        self.network_bandwidth_slider.valueChanged[int].connect(self.network_bandwidth_slider_value)
        self.network_bandwidth_slider.setMinimum(10)
        self.network_bandwidth_slider.setMaximum(150)
        self.network_bandwidth_slider.setTickInterval(10)
        self.network_bandwidth_slider.setValue(100)
        self.ants_controller.iperf_bw = 100
        self.network_bandwidth_slider.setToolTip("Bandwidth for iperf traffic, from 10Mbit/s to 150Mbit/s")
        self.network_bandwidth_slider_text = "Bandwidth: " + str(self.network_bandwidth_slider.value()) + "Mbit/s"
        self.network_bandwidth_slider_label.setText(self.network_bandwidth_slider_text)

        # Combo box for the access category
        self.access_category_field = QComboBox(self)
        self.access_category_field.addItem("Voice")
        self.access_category_field.addItem("Video")
        self.access_category_field.addItem("Best Effort")
        self.access_category_field.addItem("Background")
        self.access_category_field_label = QLabel("Access Category", self)
        self.access_category_field.activated[str].connect(self.on_access_category_change)

        # Create the iperf groupbox widget and fill it
        self.network_groupbox = QGroupBox("Network Settings")
        self.network_gridbox = QGridLayout(self)

        self.network_gridbox.addWidget(self.network_bandwidth_slider_label, 0, 0)
        self.network_gridbox.addWidget(self.network_bandwidth_slider, 0, 1)

        self.network_gridbox.addWidget(self.access_category_field_label, 1, 0)
        self.network_gridbox.addWidget(self.access_category_field, 1, 1)

        self.network_gridbox.addWidget(self.network_ap_lineedit_label, 2, 0)
        self.network_gridbox.addWidget(self.network_ap_lineedit, 2, 1)

        self.network_gridbox.addWidget(self.center_frequency_lineedit_label, 3, 0)
        self.network_gridbox.addWidget(self.center_frequency_lineedit, 3, 1)

        self.network_gridbox.addWidget(self.network_WiFi_label, 4, 0)
        self.network_gridbox.addWidget(self.network_WiFi, 4, 1)

        self.network_gridbox.addWidget(self.routing_checkbox, 5, 0)
        self.network_gridbox.addWidget(self.scan_btn, 5, 1)

        self.network_gridbox.addWidget(self.UUT_type_label, 6, 0)
        self.network_gridbox.addWidget(self.UUT_type, 6, 1)

        self.network_groupbox.setLayout(self.network_gridbox)

        # Create the USRP settings groupbox and fill it
        self.usrp_groupbox = QGroupBox("USRP Settings")
        self.usrp_gridbox = QGridLayout(self)
        self.usrp_groupbox.setLayout(self.usrp_gridbox)

        # The label and slider for setting the USRP sample rate
        # self.usrp_sample_rate_label = QLabel(None, self)
        # self.usrp_sample_rate_slider = QSlider(Qt.Horizontal, self)
        # self.usrp_sample_rate_slider.setFocusPolicy(Qt.NoFocus)
        # self.usrp_sample_rate_slider.valueChanged[int].connect(self.usrp_sample_rate_slider_value)
        # self.usrp_sample_rate_slider.setMinimum(1)
        # self.usrp_sample_rate_slider.setMaximum(20)
        # self.usrp_sample_rate_slider.setTickInterval(1)
        # self.usrp_sample_rate_slider.setValue(20)
        # self.usrp_sample_rate_slider.setToolTip("Sample rate for USRP is between 1MS/s and 20 MS/s")
        # self.usrp_sample_rate_text = "Sample rate: " + str(self.usrp_sample_rate_slider.value()) + "MS/s"
        # self.usrp_sample_rate_label.setText(self.usrp_sample_rate_text)
        # self.ants_controller.usrp_sample_rate = '20'

        # The label and slider for setting the USRP gain
        self.usrp_gain_label = QLabel(None, self)
        self.usrp_gain_slider = QSlider(Qt.Horizontal, self)
        self.usrp_gain_slider.setFocusPolicy(Qt.NoFocus)
        self.usrp_gain_slider.valueChanged[int].connect(self.usrp_gain_slider_value)
        self.usrp_gain_slider.setMinimum(1)
        self.usrp_gain_slider.setMaximum(60)
        self.usrp_gain_slider.setTickInterval(1)
        self.usrp_gain_slider.setValue(40)
        self.usrp_gain_slider.setToolTip("Gain for USRP is between 1 and 60")
        self.usrp_gain_text = "Gain: " + str(self.usrp_gain_slider.value())
        self.usrp_gain_label.setText(self.usrp_gain_text)
        self.ants_controller.usrp_gain = '40'

        # The label and slider for setting the delay between the iperf traffic start and USRP process start time
        self.usrp_run_delay_label = QLabel(None, self)
        self.usrp_run_delay_slider = QSlider(Qt.Horizontal, self)
        self.usrp_run_delay_slider.setFocusPolicy(Qt.NoFocus)
        self.usrp_run_delay_slider.valueChanged[int].connect(self.usrp_run_delay_value)
        self.usrp_run_delay_slider.setMinimum(1)
        self.usrp_run_delay_slider.setMaximum(10)
        self.usrp_run_delay_slider.setTickInterval(1)
        self.usrp_run_delay_slider.setValue(3)
        self.usrp_run_delay_slider.setToolTip("Set a delay between the time the iperf traffic starts and when the USRP runs")
        self.usrp_run_delay_text = "Run delay: " + str(self.usrp_run_delay_slider.value()) + " seconds"
        self.usrp_run_delay_label.setText(self.usrp_run_delay_text)

        # self.usrp_gridbox.addWidget(self.usrp_sample_rate_label, 0, 0)
        # self.usrp_gridbox.addWidget(self.usrp_sample_rate_slider, 0, 1)
        self.usrp_gridbox.addWidget(self.usrp_gain_label, 1, 0)
        self.usrp_gridbox.addWidget(self.usrp_gain_slider, 1, 1)
        self.usrp_gridbox.addWidget(self.usrp_run_delay_label, 2, 0)
        self.usrp_gridbox.addWidget(self.usrp_run_delay_slider, 2, 1)

        # Create the plotting groupbox and fill it
        self.plotting_groupbox = QGroupBox("Plot Settings")
        self.plotting_gridbox = QGridLayout(self)
        self.plotting_groupbox.setLayout(self.plotting_gridbox)

        # Create the general (i.e. system-level) settings groupbox

        self.general_settings_groupbox = QGroupBox("General Settings")
        self.general_settings_gridbox = QGridLayout(self)
        self.general_settings_groupbox.setLayout(self.general_settings_gridbox)

        # Checkbox to turn on or off extended debug info
        self.gs_debuginfo_checkbox = QCheckBox("Extended Debug Info",self)

        # Text box for specifying the number of sequential test runs to perform
        self.gs_number_of_runs_validator = QIntValidator(self)
        self.gs_number_of_runs_lineedit = QLineEdit(self)
        self.gs_number_of_runs_lineedit.setToolTip("Please enter an integer")
        self.gs_number_of_runs_lineedit_label = QLabel("Number of test runs",self)
        self.gs_number_of_runs_lineedit.setValidator(self.gs_number_of_runs_validator)
        self.gs_number_of_runs_lineedit.textChanged[str].connect(self.on_num_runs)

        # Add the general settings tools to the groupbox
        self.general_settings_gridbox.addWidget(self.file_name_label, 0, 0)
        self.general_settings_gridbox.addWidget(self.file_name_lineedit, 0, 1)
        self.general_settings_gridbox.addWidget(self.runtime_label, 1, 0)
        self.general_settings_gridbox.addWidget(self.runtime_slider, 1, 1)
        self.general_settings_gridbox.addWidget(self.gs_number_of_runs_lineedit_label, 2, 0)
        self.general_settings_gridbox.addWidget(self.gs_number_of_runs_lineedit, 2, 1)
        self.general_settings_gridbox.addWidget(self.gs_debuginfo_checkbox, 3, 0)
        self.general_settings_gridbox.addWidget(self.run_btn, 4, 0)
        self.general_settings_groupbox.setLayout(self.general_settings_gridbox)

        # Add the groupbox widgets to the main tab grid
        self.layout.addWidget(self.usrp_groupbox, 0, 2, 2, 1)
        self.layout.addWidget(self.network_groupbox, 0, 1, 2, 1)
        self.layout.addWidget(self.general_settings_groupbox, 0, 0, 2, 1)

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
        self.runtime_label.setText("Runtime " + str(self.ants_controller.run_time) + " seconds")

    # Allow the user to specify how many test sequences in a row to run. Set the minimum to 1
    def on_num_runs(self):
        if self.gs_number_of_runs_lineedit.text() == "":
            self.ants_controller.num_runs = 1
        elif int(self.gs_number_of_runs_lineedit.text()) < 1:
            self.ants_controller.num_runs = 1
        elif self.gs_number_of_runs_lineedit.hasAcceptableInput():
            self.ants_controller.num_runs = int(self.gs_number_of_runs_lineedit.text())

    # Checks to make sure network_ap_addr is set to a realistic IP value
    def on_ap_ip(self, text):
        if self.network_ap_lineedit.hasAcceptableInput():
            self.ants_controller.iperf_ap_addr = text

    def on_center_frequency(self, text):
        self.ants_controller.center_frequency = str(text)

    # Set file name for the test run based on what's in the box
    def on_name_change(self, text):
        self.ants_controller.file_name = text

    def on_network_WiFi_change(self, text):
        self.ants_controller.essid = text
        print ('NETWORK SELECTED IS:', self.ants_controller.essid)

    def on_UUT_type_change(self, text):
        self.ants_controller.UUT_type = text
        print ('UUT TYPE IS:', self.ants_controller.UUT_type)

    def usrp_gain_slider_value(self, value):
        self.ants_controller.usrp_gain = str(value)
        self.usrp_gain_label.setText("Gain: " + str(self.ants_controller.usrp_gain))

    def usrp_run_delay_value(self, value):
        self.ants_controller.usrp_run_delay = value
        print("Run delay set to {0} seconds\n".format(self.ants_controller.usrp_run_delay))
        self.usrp_run_delay_label.setText("Run delay: " + str(self.ants_controller.usrp_run_delay) + "seconds")

    def network_bandwidth_slider_value(self, value):
        self.ants_controller.iperf_bw = value
        print("iperf traffic bandwidth set to {0} Mbit/s\n".format(self.ants_controller.iperf_bw))
        self.network_bandwidth_slider_label.setText("Bandwidth: " + str(self.ants_controller.iperf_bw) + "Mbit/s")

    def on_timestamp_checkbox_checked(self, state):
        if state == Qt.Checked:
            pass
        else:
            pass

    def on_debug_info_checkbox_checked(self, state):
        if state == Qt.Checked:
            pass
        else:
            pass

    def on_access_category_change(self, text):
        if text == "Voice":
            self.ants_controller.access_category = 0
            print("Access category set to Voice\n")
        elif text == "Video":
            self.ants_controller.access_category = 1
            print("Access category set to Video\n")
        elif text == "Best Effort":
            self.ants_controller.access_category = 2
            print("Access category set to Best Effort\n")
        elif text == "Background":
            self.ants_controller.access_category = 3
            print("Access category set to Background\n")
        else: # Put voice in as the default in case something unexpected happens
            self.ants_controller.access_category = 0
            print("Access category set to Voice\n")

    def set_routing_button_clicked(self):
        pass

    def flush_routing_button_clicked(self):
        pass

    def configure_routing(self, state):
        if state == Qt.Checked:
            self.ants_controller.configure_routing = True
        else:
            self.ants_controller.configure_routing = False

    def scan_button_clicked(self):
        self.ants_controller.eth_name, self.ants_controller.eth_mac, self.ants_controller.wlan_name, self.ants_controller.wlan_mac, self.ants_controller.wlan_internal_name = interfaces_scan()
        networks = get_frequency_networks(self.ants_controller.wlan_name, self.ants_controller.center_frequency)
        self.ants_controller.essid = networks[0]
        print ('NETWORK SELECTED IS:', self.ants_controller.essid)
        self.network_WiFi.clear()
        for n in networks:
            self.network_WiFi.addItem(n)

    # Run the test sequence by making calls to the control.py module. run_button_clicked generates QPixmap objects to hold the .png data plots generated with matplotlib
    def run_button_clicked(self):
        self.showOverlay()
        self.control_thread = ANTS_ControlThread(self.ants_controller)
        self.control_thread.signal.connect(self.measurement_done)
        self.control_thread.start()

    def measurement_done(self):
        self.hideOverlay()

        # Update the statistics labels with the latest test sequence data
        self.results_tab.compliance_label.setText("Compliance: {0}% average over {1} runs".format(float("{0:.1f}".format(self.ants_controller.compliance_avg)), self.ants_controller.run_compliance_count))
        if self.ants_controller.run_aggression_count > 0:
            self.results_tab.aggression_label.setText("Aggression: {0}% average over {1} runs".format(float("{0:.1f}".format(self.ants_controller.aggression_avg)), self.ants_controller.run_aggression_count))
        if self.ants_controller.run_submission_count > 0:
            self.results_tab.submission_label.setText("Submission: {0}% average over {1} runs".format(float("{0:.1f}".format(self.ants_controller.submission_avg)), self.ants_controller.run_submission_count))

        # Set up the graphics for the main display

        # The general path for the data files. This is passed to each pixmap for further use
        self.results_tab.general_pixmap_path = self.ants_controller.data_dir + self.ants_controller.file_name + "_" + self.ants_controller.plotter_ac

        # The path for the bin distribution image
        self.results_tab.bin_pixmap_path = self.results_tab.general_pixmap_path + "_bin_probability.svg"
        self.results_tab.bin_pixmap = QPixmap(self.results_tab.bin_pixmap_path)

        # The path for the interframe spacing image
        self.results_tab.interframe_pixmap_path = self.results_tab.general_pixmap_path + "_interframe_spacing_histogram.svg"
        self.results_tab.interframe_pixmap = QPixmap(self.results_tab.interframe_pixmap_path)

        # The path for the raw signal image
        self.results_tab.raw_signal_pixmap_path = self.results_tab.general_pixmap_path + "_signal_magnitude_plot.svg"
        self.results_tab.raw_signal_pixmap = QPixmap(self.results_tab.raw_signal_pixmap_path)

        # The path for the transmission opportunity image
        self.results_tab.txop_pixmap_path = self.results_tab.general_pixmap_path + "_txop_durations_histogram.svg"
        self.results_tab.txop_pixmap = QPixmap(self.results_tab.txop_pixmap_path)

        print("Plots are saved as .svg files at {0}.\n".format(self.ants_controller.data_dir))

        # Set the pixmap window to be a gray background if there is no data from a previous run
        self.results_tab.graphic_label.setStyleSheet("""
            background-color: grey;
            color: white;
            font: bold;
            padding: 1px;
            border-width: 1px;
            border-style: panel;
            border-radius: 1px;
            border-color: white;
        """)
        self.results_tab.graphic_label.setPixmap(self.results_tab.bin_pixmap)

        self.ants_table.setCurrentIndex(1)
        self.ants_controller.configure_routing = False
        self.routing_checkbox.setChecked(False)

class ANTS_About_Tab(QWidget):
    def __init__(self, tabs_object, ants_controller):
        super(QWidget, self).__init__(tabs_object)
        self.ants_controller = ants_controller
        self.layout = QVBoxLayout(self)
        self.ants_message = QLabel()
        self.ants_message.setText(dedent("""\
            ANTS (the Automated Networking Test Suite) is an application written
            by the Broadband Networks Laboratory at Carleton University, with the goal of automating and simplifying
            compliance testing of wireless devices. For more information, or if you have suggestions or bugs to report,
            visit https://github.com/CarletonWirelessLab/ANTS, or contact the author directly.
            
            Icon provided by icons8.com"""))

        self.ants_message.setMargin(10)
        self.ants_message.setWordWrap(1)
        #self.setCentralWidget(self.ants_message)

        self.layout.addWidget(self.ants_message)
        self.setLayout(self.layout)

class ANTS_License_Tab(QWidget):
    def __init__(self, tabs_object, ants_controller):
        super(QWidget, self).__init__(tabs_object)
        self.ants_controller = ants_controller
        self.layout = QVBoxLayout(self)
        self.license_message = QLabel()
        self.license_message.setText(dedent("""\
            MIT License

            Copyright (c) 2018-2019 Carleton University Broadband Networks Laboratory

            Permission is hereby granted, free of charge, to any person obtaining a copy
            of this software and associated documentation files (the "Software"), to deal
            in the Software without restriction, including without limitation the rights
            to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
            copies of the Software, and to permit persons to whom the Software is
            furnished to do so, subject to the following conditions:

            The above copyright notice and this permission notice shall be included in all
            copies or substantial portions of the Software.

            THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
            IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
            FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
            AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
            LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
            OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
            SOFTWARE."""))
        self.license_message.setMargin(10)
        self.layout.addWidget(self.license_message)
        self.setLayout(self.layout)

class Advanced_GUI(QMainWindow):

    def __init__(self, ants_controller):
        super().__init__()
        
        # turn off network manager
        try:
            print("TURNING OFF NETWORK MANAGER")
            call(['nmcli', 'n', 'off'])
        except FileNotFoundError:
            print("WARNING: COULD NOT TURN OFF NETWORK MANAGER")
            pass
        
        # The ANTS Controller object
        self.ants_controller = ants_controller

        self.table_widget = ANTS_Table(self, self.ants_controller, self.showOverlay, self.hideOverlay)
        self.setCentralWidget(self.table_widget)
        self.setWindowTitle("ANTS")

        self.overlay = Overlay(self.centralWidget())
        self.overlay.hide()
        
        self.show()

    def showOverlay(self):
        self.overlay.show()

    def hideOverlay(self):
        self.overlay.hide()

    def resizeEvent(self, event):
        self.overlay.resize(event.size())
        event.accept()    

    # Make sure we get prompted before closing the GUI
    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
            "Are you sure you want to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # turn off network manager
            try:
                print("TURNING ON NETWORK MANAGER")
                call(['nmcli', 'n', 'on'])
            except FileNotFoundError:
                print("WARNING: COULD NOT TURN ON NETWORK MANAGER")
                pass

            event.accept()
        else:
            event.ignore()
