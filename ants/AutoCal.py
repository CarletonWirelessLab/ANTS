# Copyright (c) 2019 Carleton University Broadband Networks Laboratory

import sys, os
from Attenuator import Attenuator
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from iperf3 import *

import numpy as np
import matplotlib.pyplot as plt


# devices to check
devs = ["/dev/ttyACM0", "/dev/ttyACM1", "/dev/ttyACM2", "/dev/ttyACM3"]

class MainWin(QMainWindow):
	def __init__(self, client_ip, server_ip):
		super(self.__class__, self).__init__()
		self.server_ip = server_ip
		self.client_ip = client_ip
		self.setWindowTitle("USB/TTL Attenuator Auto-Calibrator")
		#self.resize(500, 500)
		self.setGeometry(100, 200, 500, 500)
		self.statusbar = self.statusBar()
		self.main_form = MainForm(self)
		self.setCentralWidget(self.main_form)

class MainForm(QWidget):
	def _dev_scan(self):
		self.n_devs = 0
		self.combo_conn.clear()
		for d in devs:
			print("Scanning for device: " + d)
			if os.path.exists(d):
				print("\t Device found.")
				self.combo_conn.addItem(d)
				self.n_devs += 1
			else:
				print("\t Device not found.")
		print(str(self.n_devs) + " devices were found.")
	def _enable_forms(self, status=True):
		self.button_calibrate.setEnabled(status)
		self.button_plot.setEnabled(status)
		self.edit_duration.setEnabled(status)
		self.edit_step.setEnabled(status)
		self.edit_server.setEnabled(status)
		self.edit_port.setEnabled(status)
		self.edit_bw.setEnabled(status)
		self.edit_bind.setEnabled(status)
		self.combo_transport.setEnabled(status)
		self.edit_tos.setEnabled(False) # XXX
	def _reset_forms(self):
		self.label_model_val.setText("N/A")
		self.label_max_attn_val.setText("N/A")
		self.label_def_step_val.setText("N/A")
		self.label_freq_val.setText("N/A")
		self.edit_step.setText("0.0")
		self.label_attn_val.setText("N/A")
		self.win.statusbar.showMessage("Ready.")
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
		self.button_conn = QPushButton("Connect")
		self.button_conn.setToolTip("Connect to an USB/TTL attenuator device")
		self.button_conn.clicked.connect(self.button_conn_clicked)
		self.button_refresh = QPushButton("Refresh")
		self.button_refresh.clicked.connect(self.button_refresh_clicked)
		self.layout_conn.addWidget(self.label_conn, 0, 0)
		self.layout_conn.addWidget(self.combo_conn, 0, 1)
		self.layout_conn.addWidget(self.button_refresh, 1, 1)
		self.layout_conn.addWidget(self.button_conn, 2, 1)
		# device information labels
		self.group_info = QGroupBox("Device Information")
		self.layout.addWidget(self.group_info)
		self.layout_labels = QGridLayout()
		self.group_info.setLayout(self.layout_labels)
		self.label_model = QLabel("Model:")
		self.label_model_val = QLabel()
		self.label_max_attn = QLabel("Maximum attenuation:")
		self.label_max_attn_val = QLabel()
		self.label_def_step = QLabel("Default step size:")
		self.label_def_step_val = QLabel()
		self.label_freq = QLabel("Frequency:")
		self.label_freq_val = QLabel()
		self.layout_labels.addWidget(self.label_model, 0, 0)
		self.layout_labels.addWidget(self.label_model_val, 0, 1)
		self.layout_labels.addWidget(self.label_max_attn, 1, 0)
		self.layout_labels.addWidget(self.label_max_attn_val, 1, 1)
		self.layout_labels.addWidget(self.label_def_step, 2, 0)
		self.layout_labels.addWidget(self.label_def_step_val, 2, 1)
		self.layout_labels.addWidget(self.label_freq, 3, 0)
		self.layout_labels.addWidget(self.label_freq_val, 3, 1)
		# iperf settings
		self.group_iperf = QGroupBox("Traffic Generator Settings")
		self.layout.addWidget(self.group_iperf)
		self.layout_iperf = QGridLayout()
		self.group_iperf.setLayout(self.layout_iperf)
		self.label_bw = QLabel("Bandwidth:")
		self.edit_bw = QLineEdit("100")
		self.label_bw2 = QLabel("Mbps")
		self.label_bind = QLabel("Client:")
		self.edit_bind = QLineEdit(win.client_ip)
		self.label_transport = QLabel("Transport:")
		self.combo_transport = QComboBox()
		self.combo_transport.addItem("TCP")
		self.combo_transport.addItem("UDP")
		self.label_tos = QLabel("ToS:")
		self.edit_tos = QLineEdit("0")
		self.label_server = QLabel("Server:")
		self.edit_server = QLineEdit(win.server_ip)
		self.label_port = QLabel("Port:")
		self.edit_port = QLineEdit("5201")
		# calibration configurations
		self.group_conf = QGroupBox("Device Calibration Settings")
		self.layout.addWidget(self.group_conf)
		self.layout_calibrate = QGridLayout()
		self.group_conf.setLayout(self.layout_calibrate)
		self.label_step = QLabel("Step size:")
		self.edit_step = QLineEdit("0.0")
		self.label_step2 = QLabel("dB")
		self.label_duration = QLabel("Duration:")
		self.edit_duration = QLineEdit("2")
		self.label_duration2 = QLabel("sec/step")
		self.label_attn = QLabel("Attenuation:")
		self.label_attn_val = QLabel("0 dB")
		self.button_calibrate = QPushButton("Auto-Calibrate")
		self.button_calibrate.setToolTip("Automatically calibrate the attenuator device")
		self.button_calibrate.clicked.connect(self.button_calibrate_clicked)
		self.button_plot = QPushButton("Plot")
		self.button_plot.setToolTip("Plot a graph with the calibration results")
		self.button_plot.clicked.connect(self.button_plot_clicked)
		self._dev_scan()
		if self.n_devs:
			self.button_conn.setEnabled(True)
		else:
			self.button_conn.setEnabled(False)
		self._enable_forms(False)
		self._reset_forms()
		self.layout_iperf.addWidget(self.label_bw, 0, 0)
		self.layout_iperf.addWidget(self.edit_bw, 0, 1)
		self.layout_iperf.addWidget(self.label_bw2, 0, 2)
		self.layout_iperf.addWidget(self.label_bind, 1, 0)
		self.layout_iperf.addWidget(self.edit_bind, 1, 1)
		self.layout_iperf.addWidget(self.label_transport, 2, 0)
		self.layout_iperf.addWidget(self.combo_transport, 2, 1)
		self.layout_iperf.addWidget(self.label_tos, 3, 0)
		self.layout_iperf.addWidget(self.edit_tos, 3, 1)
		self.layout_iperf.addWidget(self.label_server, 4, 0)
		self.layout_iperf.addWidget(self.edit_server, 4, 1)
		self.layout_iperf.addWidget(self.label_port, 4, 2)
		self.layout_iperf.addWidget(self.edit_port, 4, 3)
		self.layout_calibrate.addWidget(self.label_step, 0, 0)
		self.layout_calibrate.addWidget(self.edit_step, 0, 1)
		self.layout_calibrate.addWidget(self.label_step2, 0, 2)
		self.layout_calibrate.addWidget(self.label_duration, 1, 0)
		self.layout_calibrate.addWidget(self.edit_duration, 1, 1)
		self.layout_calibrate.addWidget(self.label_duration2, 1, 2)
		self.layout_calibrate.addWidget(self.label_attn, 2, 0)
		self.layout_calibrate.addWidget(self.label_attn_val, 2, 1)
		self.layout_calibrate.addWidget(self.button_calibrate, 3, 1)
		self.layout_calibrate.addWidget(self.button_plot, 3, 2)
		self.last_run_results = []	# used only for plots
	def button_conn_clicked(self):
		self.button_calibrate.setEnabled(False)
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
			self.label_max_attn_val.setText(str(self.attn.getMaxAttn()) + " dB")
			self.label_def_step_val.setText(str(self.attn.getDefStepSize()) + " dB")
			self.label_freq_val.setText(self.attn.getFrequency())
			self.edit_step.setText(str(self.attn.getStepSize()))
			print(("Current attenuation: " + str(self.attn.getAttenuation())))
			self.label_attn_val.setText(str(self.attn.getAttenuation()) + " dB")
			self.win.statusbar.showMessage("Device connected successfully.")
			self.button_calibrate.setEnabled(True)
			self._enable_forms(True)
		else:
			print("Error: no such device.")
			self.win.statusbar.showMessage("Error: no such device.")
			self._enable_forms(False)
			self._reset_forms()
	def button_refresh_clicked(self):
		self._dev_scan()
		if self.n_devs:
			self.button_conn.setEnabled(True)
		else:
			self.button_conn.setEnabled(False)
		self._enable_forms(False)
		self._reset_forms()
	def button_calibrate_clicked(self):
		a = 0.0
		best_attn = 0.0
		best_bps = 0.0
		mx = self.attn.getMaxAttn()
		delta = float(self.edit_step.text())
		duration = int(self.edit_duration.text())
		bandwidth = int(self.edit_bw.text()) * 1000000	# Mbps
		bind = self.edit_bind.text()
		server = self.edit_server.text()
		port = self.edit_port.text()
		transport = str(self.combo_transport.currentText()).lower()
		if self.attn.setStepSize(delta):
			print("setStepSize: " + str(delta) + " SUCCESS")
		else:
			print("setStepSize: " + str(delta) + " FAILED")
		print("Starting auto-calibration test...")
		if self.attn.setAttenuation(0.0):
			print("\tsetAttenuation: 0.0 dB SUCCESS")
		else:
			print("\tsetAttenuation: 0.0 dB FAILED")
		self.win.statusbar.showMessage("Auto-calibrating device ... Please be patient!")
		print("\tBandwidth: " + str(bandwidth) + " bps")
		del self.last_run_results[:]	# used only for plots
		while a < mx:
			print("\tTrying attenuation of " + str(a) + " dB")
			try:
				client = iperf3.Client()
				client.duration = duration
				client.bandwidth = bandwidth
				client.bind_address = bind
				client.server_hostname = server
				client.port = port
				client.transport = transport
				result = client.run()
				if result.error:
					print("\t\tresult error: " + result.error)
					#print "\t\tResults: " + str(result)
				else:
					bps = int(result.received_bps)
					kbps = bps / 1000.0
					mbps = kbps / 1000.0
					print("\t\t" + str(bps) + " bps were received.")
					print("\t\t" + str(mbps) + " Mbps (" + str(kbps) + " Kbps) were received.")
					self.last_run_results.append((a, bps))	# used only for plots
					if bps > best_bps:
						best_bps = bps
						best_attn = a
					del result
					del client
			except OSError as e:
				print("\t\tiperf error: " + str(e))
			#except:
			#	print "\t\tiperf3 error."
			self.attn.increment()
			# TODO: a = getAttenuation()
			a += delta
		# set attentuation to the best attenuation value
		if self.attn.setAttenuation(best_attn):
			print("setAttenuation (best bps): " + str(best_attn) + " SUCCESS")
			self.label_attn_val.setText(str(best_attn) + " dB")
			self.win.statusbar.showMessage("Device auto-calibrated to " + str(best_attn) + " dB (" + str(best_bps) + " bps) successfully.")
		else:
			print("setAttenuation (best bps): " + str(best_attn) + " FAILED")
	def button_plot_clicked(self):
		if not self.last_run_results:
			print("No calibration results to plot")
			return
		print("Calibration details:")
		for r in self.last_run_results:
			print("\t" + str(r[0]) + ", " + str(r[1]))
		x_list = [r[0] for r in self.last_run_results]
		y_list = [r[1] for r in self.last_run_results]
		plt.plot(x_list, y_list, '.-')
		plt.title('Bandwidth vs Attenuation')
		plt.xlabel('Attenuation (dB)')
		plt.ylabel('Bandwidth (bps)')
		plt.show()

def main():
	app = QApplication(sys.argv)
	main_win = MainWin()
	main_win.show()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()
