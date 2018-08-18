#/usr/bin/python3

from control import ANTS_Controller
from simplegui import Simple_GUI
from advancedgui import Advanced_GUI
from PyQt5.QtWidgets import QApplication
import sys


if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = ANTS_Controller()
    gui = Advanced_GUI(controller)
    sys.exit(app.exec_())