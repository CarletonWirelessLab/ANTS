#/usr/bin/python3

from sigcontrol import SiGPyC_Controller
from simplegui import Simple_GUI
from PyQt5.QtWidgets import QApplication
import sys


if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = SiGPyC_Controller()
    gui = Simple_GUI(controller)
    sys.exit(app.exec_())
