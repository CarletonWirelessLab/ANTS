#/usr/bin/python3

from sigcontrol import SiGPyC_Controller
from siggui import SiGPyC_GUI
from PyQt5.QtWidgets import QApplication
import sys


if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = SiGPyC_Controller()
    gui = SiGPyC_GUI(controller)
    sys.exit(app.exec_())
