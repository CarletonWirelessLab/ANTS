# Copyright (c) 2019 Carleton University Broadband Networks Laboratory

import sys, os
from Attenuator import Attenuator
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

# devices to check\
devs = ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2", "/dev/ttyACM3"]

class MainWin(QMainWindow):
	def __init__(self):
		super(self.__class__, self).__init__()
		self.setWindowTitle("USB/TTL Attenuator Control Panel")
		#self.resize(400, 400)
		self.setGeometry(100, 200, 400, 400)
		self.statusbar = self.statusBar()
		self.statusbar.showMessage('Ready.')
		self.main_form = MainForm(self)
		self.setCentralWidget(self.main_form)

class MainForm(QWidget):
	def __init__(self, win):
		super(self.__class__, self).__init__()
		self.win = win
		self.layout = QVBoxLayout()
		self.setLayout(self.layout)
		# connection settings
		self.group_conn = QGroupBox("Connection Settings")
		self.layout.addWidget(self.group_conn)
		self.layout_conn = QGridLayout()
		self.group_conn.setLayout(self.layout_conn)
		self.label_conn = QLabel("Device:")
		self.combo_conn = QComboBox()	
		for d in devs:
			print("Scanning for device: " + d)
			if os.path.exists(d):
				print("\tDevice found.")
				self.combo_conn.addItem(d)
			else:
				print("\tDevice not found.")
		self.button_conn = QPushButton("Connect")
		self.button_conn.setToolTip("Connect to an USB/TTL attenuator device")
		self.button_conn.clicked.connect(self.button_conn_clicked)
		self.layout_conn.addWidget(self.label_conn, 0, 0)
		self.layout_conn.addWidget(self.combo_conn, 0, 1)
		self.layout_conn.addWidget(self.button_conn, 1, 1)
		# device information labels
		self.group_info = QGroupBox("Device Information")
		self.layout.addWidget(self.group_info)
		self.layout_labels = QGridLayout()
		self.group_info.setLayout(self.layout_labels)
		self.label_model = QLabel("Model:")
		self.label_model_val = QLabel("")
		self.label_max_attn = QLabel("Max attenuation:")
		self.label_max_attn_val = QLabel("")
		self.label_def_step = QLabel("Default step size:")
		self.label_def_step_val = QLabel("")
		self.label_freq = QLabel("Frequency:")
		self.label_freq_val = QLabel("")
		self.layout_labels.addWidget(self.label_model, 0, 0)
		self.layout_labels.addWidget(self.label_model_val, 0, 1)
		self.layout_labels.addWidget(self.label_max_attn, 1, 0)
		self.layout_labels.addWidget(self.label_max_attn_val, 1, 1)
		self.layout_labels.addWidget(self.label_def_step, 2, 0)
		self.layout_labels.addWidget(self.label_def_step_val, 2, 1)
		self.layout_labels.addWidget(self.label_freq, 3, 0)
		self.layout_labels.addWidget(self.label_freq_val, 3, 1)
		# configurations
		self.group_conf = QGroupBox("Device Configuration")
		self.layout.addWidget(self.group_conf)
		self.layout_config = QGridLayout()
		self.group_conf.setLayout(self.layout_config)
		self.label_attn = QLabel("Attenuation")
		self.slider_attn = QSlider(Qt.Horizontal)
		self.slider_attn.setTickInterval(1)
		#self.slider_attn.setTickPosition(QSlider.TicksBothSides)
		self.slider_attn.setMinimum(0)
		self.slider_attn.setMaximum(0)
		self.slider_attn.valueChanged[int].connect(self.slider_attn_changed)
		self.label_attn_val = QLabel("0 db")
		self.button_config = QPushButton("Configure")
		self.button_config.setToolTip("Configure the attenuator device")
		self.button_config.clicked.connect(self.button_config_clicked)
		self.button_config.setEnabled(False)
		self.layout_config.addWidget(self.label_attn, 0, 0)
		self.layout_config.addWidget(self.slider_attn, 0, 1)
		self.layout_config.addWidget(self.label_attn_val, 0, 2)
		self.layout_config.addWidget(self.button_config, 1, 1)
	def button_conn_clicked(self):
		self.button_config.setEnabled(False)
		dev = str(self.combo_conn.currentText())
		self.attn = Attenuator(dev)
		print("Trying " + dev)
		if self.attn.ready():
			print("Device connected successfully.")
			print("Device model: " + self.attn.getModel())
			print("Device max attenuation: " + str(self.attn.getMaxAttn()))
			print("Device default step size: " + str(self.attn.getDefStepSize()))
			print("Device frequency: " + self.attn.getFrequency())
			self.label_model_val.setText(self.attn.getModel())
			self.label_max_attn_val.setText(str(self.attn.getMaxAttn()) + " db")
			self.label_def_step_val.setText(str(self.attn.getDefStepSize()) + " db")
			self.label_freq_val.setText(self.attn.getFrequency())
			# update attenuation slider
			self.slider_attn.setMaximum(self.attn.getMaxAttn())
			if self.attn.setStepSize(1):
				print("setStepSize: 1 SUCCESS")
			else:
				print("setStepSize: 1 FAILED")
			print(("Current attenuation: " + str(self.attn.getAttenuation())))
			self.slider_attn.setValue(int(self.attn.getAttenuation()))
			self.win.statusbar.showMessage("Device connected successfully.")
			self.button_config.setEnabled(True)
		else:
			print("Error: no such device.")
			self.win.statusbar.showMessage("Error: no such device.")
	def button_config_clicked(self):
		# set attentuation to value
		if self.attn.setAttenuation(self.attn_value):
			print("setAttenuation: " + str(self.attn_value) + " SUCCESS")
			self.win.statusbar.showMessage("Device attenuation set to " + str(self.attn_value) + " db successfully.")
		else:
			print("setAttenuation: " + str(self.attn_value) + " FAILED")
	def slider_attn_changed(self, value):
		self.attn_value = value
		self.label_attn_val.setText(str(self.attn_value) + " db")

def main():
	app = QApplication(sys.argv)
	main_win = MainWin()
	main_win.show()
	sys.exit(app.exec_())
	
if __name__ == "__main__":
	main()
