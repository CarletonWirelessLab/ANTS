#/usr/bin/python3

from sigcontrol import SiGPyC_Controller
from siggui import SiGPyC_GUI
from PyQt5.QtWidgets import QWidget, QCheckBox, QApplication, QComboBox, QMessageBox, QPushButton, QMainWindow, QLineEdit, QSlider, QLabel
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QRegExpValidator
import sys
import subprocess
import threading
import time
import queue
import os
import matlab.engine


if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = SiGPyC_Controller()
    gui = SiGPyC_GUI(controller)
    sys.exit(app.exec_())
