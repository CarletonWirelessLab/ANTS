
from PyQt5.QtWidgets import QWidget, QDialog, QMenuBar, QCheckBox, QAction, QApplication, QComboBox, QMessageBox, QPushButton, QMainWindow, QLineEdit, QSlider, QLabel, QGridLayout, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
import sys

class Menu():

    def __init__(self):
            super().__init__()

            self.initUI()


    def initUI(self):

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

if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = Menu()
    sys.exit(app.exec_())
