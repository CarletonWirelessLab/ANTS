#!/usr/bin/python3

from PyQt5.QtWidgets import QWidget, QDialog, QMenuBar, QCheckBox, QAction
from PyQt5.QtWidgets import QApplication, QComboBox, QMessageBox, QPushButton
from PyQt5.QtWidgets import QMainWindow, QLineEdit, QSlider, QLabel, QGridLayout
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QRadioButton, QTabWidget
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtCore import Qt, QRegExp, QSettings
from PyQt5.QtGui import QRegExpValidator, QPixmap, QIntValidator

# The parent "table" class that holds all of the functional tabs
class ANTS_Table(QWidget):

    def __init__(self, main_gui, ants_controller):
        super(QWidget, self).__init__(main_gui)

        # Initialize the ANTS controller object to run the tests
        self.ants_controller = ants_controller

        # Set the layout type for the GUI and instantiate the tabs widget
        self.layout = QVBoxLayout(self)
        self.tabs = QTabWidget()

        # Instantiate all of the tab objects needed for the GUI
        self.results_tab = ANTS_Results_Tab(self, self.ants_controller)
        self.settings_tab = ANTS_Settings_Tab(self, self.ants_controller)
        self.about_tab = ANTS_About_Tab(self, self.ants_controller)
        self.license_tab = ANTS_License_Tab(self, self.ants_controller)
        self.tabs.resize(300, 200)

        self.tabs.addTab(self.results_tab, "Results")
        self.tabs.addTab(self.settings_tab, "Control Settings")
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

        # Create a text box to take the filename used by the USRP and converter
        # tools
        self.file_name_lineedit = QLineEdit(self)
        self.file_name_lineedit.textChanged[str].connect(self.on_name_change)
        self.file_name_lineedit.setToolTip("The filename for the USRP to output the data to")
        self.file_name_text = "Filename"
        self.file_name_label = QLabel(self.file_name_text, self)
        self.layout.addWidget(self.file_name_label, 0, 6, 1, 1)
        self.layout.addWidget(self.file_name_lineedit, 1, 6, 1, 1)
        self.layout.addWidget(self.graphic_label, 0, 0, 5, 5)

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

        self.layout.addWidget(self.runtime_label, 2, 6, 1, 1)
        self.layout.addWidget(self.runtime_slider, 3, 6, 1, 1)

        # The button for running the entire sequence
        self.run_btn = QPushButton('Run', self)
        self.run_btn.setToolTip('Run the test sequences selected')
        self.run_btn.resize(self.run_btn.sizeHint())
        self.run_btn.clicked.connect(self.run_button_clicked)

        self.layout.addWidget(self.run_btn, 4, 6, 1, 1)

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

    # Set file name based on what's in the box
    def on_name_change(self, text):

        self.ants_controller.file_name = text

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

    # Run the test sequence by making calls to the control.py module. run_button_clicked generates QPixmap objects to hold the .png data plots generated with matplotlib
    def run_button_clicked(self):
        self.ants_controller.start_usrp_iperf()
        self.ants_controller.make_plots()

        # Set up the graphics for the main display

        # The general path for the data files. This is passed to each pixmap for further use
        self.general_pixmap_path = self.ants_controller.data_dir + self.ants_controller.file_name + "_" + self.ants_controller.plotter_ac

        # The path for the bin distribution image
        self.bin_pixmap_path = self.general_pixmap_path + "_bin_probability.png"
        self.bin_pixmap = QPixmap(self.bin_pixmap_path)

        # The path for the interframe spacing image
        self.interframe_pixmap_path = self.general_pixmap_path + "_interframe_spacing_histogram.png"
        self.interframe_pixmap = QPixmap(self.interframe_pixmap_path)

        # The path for the raw signal image
        self.raw_signal_pixmap_path = self.general_pixmap_path + "_signal_magnitude_plot.png"
        self.raw_signal_pixmap = QPixmap(self.raw_signal_pixmap_path)

        # The path for the transmission opportunity image
        self.txop_pixmap_path = self.general_pixmap_path + "_txop_durations_histogram.png"
        self.txop_pixmap = QPixmap(self.txop_pixmap_path)

        print("Plots are saved as .png files at {0}.\n".format(self.ants_controller.data_dir))

        # Set the pixmap window to be a gray background if there is no data from a previous run
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
        self.graphic_label.setPixmap(self.bin_pixmap)

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

# The catch-all tab widget for settings related to ANTS. Data entered here should be passed to the ANTS controller object
class ANTS_Settings_Tab(QWidget):
    def __init__(self, tabs_object, ants_controller):
        super(QWidget, self).__init__(tabs_object)
        self.ants_controller = ants_controller

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

        # Text box for specifying the iperf client IPv4 address. Uses the ip validator object to verify a valid IP is given
        self.iperf_client_lineedit = QLineEdit(self)
        self.iperf_client_lineedit_label = QLabel("Client IP", self)
        self.iperf_client_lineedit.setValidator(self.ip_validator)
        self.iperf_client_lineedit.textChanged[str].connect(self.on_client_ip)

        # Text box for specifying the iperf server IPv4 address. Uses the ip validator object to verify a valid IP is given
        self.iperf_server_lineedit = QLineEdit(self)
        self.iperf_server_lineedit_label = QLabel("Server IP", self)
        self.iperf_server_lineedit.setValidator(self.ip_validator)
        self.iperf_server_lineedit.textChanged[str].connect(self.on_server_ip)

        # Specify the iperf type-of-service value (client only)
        self.iperf_TOS_field = QComboBox(self)
        self.iperf_TOS_field.addItem("Minimize delay (0x10)")
        self.iperf_TOS_field.addItem("Maximize throughput (0x08)")
        self.iperf_TOS_field.addItem("Maximize reliability (0x04)")
        self.iperf_TOS_field.addItem("Minimize cost (0x02)")
        self.iperf_TOS_field_label = QLabel("TOS", self)
        self.iperf_TOS_field.activated[str].connect(self.on_iperf_TOS_field_change)

        # Set the iperf bandwidth value (client only)
        self.iperf_bandwidth_field = QLineEdit(self)
        self.iperf_bandwidth_field_label = QLabel("Bandwidth", self)
        self.iperf_bandwidth_field.textChanged[str].connect(self.on_iperf_bandwidth_field_change)

        # Create the iperf groupbox widget and fill it
        self.iperf_groupbox = QGroupBox("iperf Settings")
        self.iperf_gridbox = QGridLayout(self)
        self.iperf_gridbox.addWidget(self.iperf_client_lineedit_label, 0, 0)
        self.iperf_gridbox.addWidget(self.iperf_client_lineedit, 0, 1)
        self.iperf_gridbox.addWidget(self.iperf_TOS_field_label, 1, 0)
        self.iperf_gridbox.addWidget(self.iperf_TOS_field, 1, 1)
        self.iperf_gridbox.addWidget(self.iperf_bandwidth_field_label, 2, 0)
        self.iperf_gridbox.addWidget(self.iperf_bandwidth_field, 2, 1)
        self.iperf_gridbox.addWidget(self.iperf_server_lineedit_label, 3, 0)
        self.iperf_gridbox.addWidget(self.iperf_server_lineedit, 3, 1)
        self.iperf_groupbox.setLayout(self.iperf_gridbox)

        # Create the USRP settings groupbox and fill it
        self.usrp_groupbox = QGroupBox("USRP Settings")
        self.usrp_gridbox = QGridLayout(self)
        self.usrp_groupbox.setLayout(self.usrp_gridbox)
        self.usrp_sample_rate_slider = QSlider(Qt.Horizontal, self)
        self.usrp_sample_rate_slider.setFocusPolicy(Qt.NoFocus)
        self.usrp_sample_rate_slider.valueChanged[int].connect(self.usrp_slider_value)
        self.usrp_sample_rate_slider.setMinimum(0)
        self.usrp_sample_rate_slider.setMaximum(20)
        self.usrp_sample_rate_slider.setTickInterval(1)
        self.usrp_sample_rate_slider.setValue(20)
        self.usrp_sample_rate_slider.setToolTip("Sample rate for USRP is between 1MS/s and20 MS/s")
        self.usrp_sample_rate_text = "Sample rate: " + str(self.usrp_sample_rate_slider.value()) + "MS/s"
        self.usrp_sample_rate_label = QLabel(self.usrp_sample_rate_text,self)

        self.usrp_run_delay_slider = QSlider(Qt.Horizontal, self)
        self.usrp_run_delay_slider.setFocusPolicy(Qt.NoFocus)
        self.usrp_run_delay_slider.valueChanged[int].connect(self.usrp_run_delay_value)
        self.usrp_run_delay_slider.setMinimum(0)
        self.usrp_run_delay_slider.setMaximum(10)
        self.usrp_run_delay_slider.setTickInterval(1)
        self.usrp_run_delay_slider.setValue(3)
        self.usrp_run_delay_slider.setToolTip("Sample rate for USRP is between 1MS/s and20 MS/s")
        self.usrp_run_delay_text = "Run delay: " + str(self.usrp_run_delay_slider.value()) + " seconds"
        self.usrp_run_delay_label = QLabel(self.usrp_run_delay_text, self)

        self.usrp_gridbox.addWidget(self.usrp_sample_rate_label, 0, 0)
        self.usrp_gridbox.addWidget(self.usrp_sample_rate_slider, 0, 1)
        self.usrp_gridbox.addWidget(self.usrp_run_delay_label, 1, 0)
        self.usrp_gridbox.addWidget(self.usrp_run_delay_slider, 1, 1)

        # Create the plotting groupbox and fill it
        self.plotting_groupbox = QGroupBox("Plot Settings")
        self.plotting_gridbox = QGridLayout(self)
        self.plotting_groupbox.setLayout(self.plotting_gridbox)

        # Create the general (i.e. system-level) settings groupbox
        self.general_settings_groupbox = QGroupBox("General Settings")
        self.general_settings_gridbox = QGridLayout(self)
        self.general_settings_groupbox.setLayout(self.general_settings_gridbox)

        # Checkbox to turn on or off timestamping of test run folders
        self.gs_timestamp_checkbox = QCheckBox("Timestamp Test Folders",self)

        # Checkbox to turn on or off extended debug info
        self.gs_debuginfo_checkbox = QCheckBox("Extended Debug Info",self)

        # Text box for specifying the number of sequential test runs to perform
        self.gs_number_of_runs_validator = QIntValidator(self)
        self.gs_number_of_runs_lineedit = QLineEdit(self)
        self.gs_number_of_runs_lineedit.setToolTip("Please enter an integer")
        self.gs_number_of_runs_lineedit_label = QLabel("Number of test runs",self)
        self.gs_number_of_runs_lineedit.setValidator(self.gs_number_of_runs_validator)

        # Combo box for the access category
        self.access_category_field = QComboBox(self)
        self.access_category_field.addItem("Voice")
        self.access_category_field.addItem("Video")
        self.access_category_field.addItem("Best Effort")
        self.access_category_field.addItem("Background")
        self.access_category_field_label = QLabel("Access Category", self)
        self.access_category_field.activated[str].connect(self.on_access_category_change)

        # Add the general settings tools to the groupbox
        self.general_settings_gridbox.addWidget(self.gs_timestamp_checkbox, 2, 0)
        self.general_settings_gridbox.addWidget(self.gs_debuginfo_checkbox, 3, 0)
        self.general_settings_gridbox.addWidget(self.gs_number_of_runs_lineedit_label, 4, 0)
        self.general_settings_gridbox.addWidget(self.gs_number_of_runs_lineedit, 4, 1)
        self.general_settings_gridbox.addWidget(self.access_category_field_label, 1, 0)
        self.general_settings_gridbox.addWidget(self.access_category_field, 1, 1)
        self.general_settings_groupbox.setLayout(self.general_settings_gridbox)

        # Add the groupbox widgets to the main tab grid
        self.layout.addWidget(self.usrp_groupbox, 0, 2, 2, 1)
        self.layout.addWidget(self.iperf_groupbox, 0, 1, 2, 1)
        self.layout.addWidget(self.general_settings_groupbox, 0, 0, 2, 1)

    # Action methods for access category radio buttons
    def on_ac_voice_clicked(self):
        self.ants_controller.access_category = 0
        print("Access category set to voice\n")

    def on_ac_video_clicked(self):
        self.ants_controller.access_category = 1
        print("Access category set to video\n")

    def on_ac_besteffort_clicked(self):
        self.ants_controller.access_category = 2
        print("Access category set to best effort\n")

    def on_ac_background_clicked(self):
        self.ants_controller.access_category = 3
        print("Access category set to background\n")

    # Checks to make sure iperf_client_addr is set to a realistic IP value
    def on_client_ip(self, text):
        if self.iperf_client_lineedit.text == "":
            self.iperf_client_lineedit.text = "10.1.11.115"
        elif self.iperf_client_lineedit.hasAcceptableInput():
            self.ants_controller.iperf_client_addr = text

    # Checks to make sure iperf_server_addr is set to a realistic IP value
    def on_server_ip(self, text):
        if self.iperf_server_lineedit.text == "":
            self.iperf_server_lineedit.text = "10.1.1.120"
        elif self.iperf_server_lineedit.hasAcceptableInput():
            self.ants_controller.iperf_server_addr = text

    # Set file name for the test run based on what's in the box
    def on_name_change(self, text):

        self.ants_controller.file_name = text

    def on_iperf_TOS_field_change(self, text):
        pass

    def on_iperf_bandwidth_field_change(self, text):
        pass

    def usrp_slider_value(self, value):
        if value == 0:
            self.ants_controller.usrp_sample_rate_value = 1
            print("Sample rate set to {0} MS/s\n".format(self.ants_controller.usrp_sample_rate_value))
        elif value == 20:
            self.ants_controller.usrp_sample_rate_value = 20
            print("Sample rate set to {0} MS/s\n".format(self.ants_controller.usrp_sample_rate_value))
        else:
            self.ants_controller.usrp_sample_rate_value = value
            print("Sample rate set to {0} MS/s\n".format(self.ants_controller.usrp_sample_rate_value))
        self.usrp_sample_rate_label.setText("Sample rate: " + str(self.ants_controller.usrp_sample_rate_value) + "MS/s")

    def usrp_run_delay_value(self, value):
        if value == 0:
            self.ants_controller.usrp_run_delay = 1
            print("Run delay set to {0} seconds\n".format(self.ants_controller.usrp_run_delay))
        elif value == 20:
            self.ants_controller.usrp_run_delay = 10
            print("Run delay set to {0} seconds\n".format(self.ants_controller.usrp_run_delay))
        else:
            self.ants_controller.usrp_run_delay = value
            print("Run delay set to {0} seconds\n".format(self.ants_controller.usrp_run_delay))
        self.usrp_run_delay_label.setText("Run delay: " + str(self.ants_controller.usrp_run_delay) + "seconds")

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


class ANTS_About_Tab(QWidget):
    def __init__(self, tabs_object, ants_controller):
        super(QWidget, self).__init__(tabs_object)
        self.ants_controller = ants_controller
        self.layout = QVBoxLayout(self)
        self.ants_message = QLabel()
        self.ants_message.setText("ANTS (the Automated Networking Test Suite) is an application written \
by the Broadband Networks Laboratory at Carleton University, with the goal of automating and simplifying \
compliance testing of wireless devices. For more information, or if you have suggestions or bugs to report, \
visit https://github.com/CarletonWirelessLab/ANTS, or contact the author directly.\n")

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
        self.license_message.setText("MIT License\n\
\n\
Copyright (c) 2018-2019 Carleton University Broadband Networks Laboratory\n\
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
        self.layout.addWidget(self.license_message)
        self.setLayout(self.layout)

class Advanced_GUI(QMainWindow):

    def __init__(self, ants_controller):
        super().__init__()

        # The ANTS Controller object
        self.ants_controller = ants_controller

        self.table_widget = ANTS_Table(self, self.ants_controller)
        self.setCentralWidget(self.table_widget)

        self.show()

    # Make sure we get prompted before closing the GUI
    def closeEvent(self, event):

        reply = QMessageBox.question(self, 'Message',
            "Are you sure you want to quit?", QMessageBox.Yes |
            QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
