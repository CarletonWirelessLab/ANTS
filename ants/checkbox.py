from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import inspect
import os

class Try(QWidget):

    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):
        checkboxList =[]

        # The checkbox for enabling the USRP
        self.usrp_checkbox = QCheckBox('USRP', self)
        self.usrp_checkbox.move(20, 20)
        self.usrp_checkbox.setToolTip("Sense traffic on the wireless medium")

        # The checkbox for the conversion tool
        self.converter_checkbox = QCheckBox('Convert', self)
        self.converter_checkbox.move(20, 140)
        self.converter_checkbox.setToolTip("Convert the output file")

        # The checkbox for the plotting tool
        self.plotter_checkbox = QCheckBox('Plot', self)
        self.plotter_checkbox.move(20, 200)
        self.plotter_checkbox.setToolTip("Plot the WiFi traffic")



        self.setGeometry(500, 500, 400, 300)
        self.setWindowTitle('QCheckBox')
        self.show()

        # Get settings
        settings = QSettings()
        # Get checkbox state with speciying type of checkbox:
        # type=bool is a replacement of toBool() in PyQt5
        check_usrp_checkbox = settings.value('usrp_checkbox',False, type=bool)
        check_converter = settings.value('converter_checkbox',False, type=bool)

        # Set state
        self.usrp_checkbox.setChecked(check_usrp_checkbox)
        self.converter_checkbox.setChecked(check_converter)

        # connect the slot to the signal by clicking the checkbox to save the state settings
        self.usrp_checkbox.clicked.connect(self.save_check_usrp_checkbox_settings)
        self.converter_checkbox.clicked.connect(self.save_converter_checkbox_settings)


    # Slot checkbox to save the settings
    def save_check_usrp_checkbox_settings(self):
        settings = QSettings()
        settings.setValue('usrp_checkbox', self.usrp_checkbox.isChecked())
        settings.sync()


    # Slot checkbox to save the settings
    def save_converter_checkbox_settings(self):
        settings = QSettings()
        settings.setValue('converter_checkbox', self.converter_checkbox.isChecked())
        settings.sync()


# def guisave(self):
#     self.settings.setValue('size', self.size())
#     self.settings.setValue('pos', self.pos())
#
#
#     for name, obj in inspect.getmembers(self):
#         if isinstance(obj, QCheckBox):
#             name = obj.objectName()
#             state = obj.isChecke d()
#             settings.setValue(name, state)
#
# def guirestore(self):
#     self.resize(self.settings.value('size', QtCore.QSize(500, 500)))
#     self.move(self.settings.value('pos', QtCore.QPoint(60, 60)))
#
#     for name, obj in inspect.getmembers(self):
#         if isinstance(obj, QCheckBox):
#             name = obj.objectName();
#             value = settings.value(name)  # get stored value from registr
#         if value != None:
#             obj.setChecked(strtobool(value))  # restore checkbox



if __name__ == '__main__':

    app = QApplication(sys.argv)
#    guirestore(ex.settings)
    ex = Try()
#    guirestore(ex.settings)

    #guisave(ex)

    sys.exit(app.exec_())
#    guisave(ex.settings)
