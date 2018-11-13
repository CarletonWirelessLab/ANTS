from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QCheckBox, QGridLayout, QLabel, QSpacerItem, \
    QSizePolicy
from PyQt5.QtCore import QSize, QCoreApplication, QSettings


ORGANIZATION_NAME = 'Example App'
ORGANIZATION_DOMAIN = 'example.com'
APPLICATION_NAME = 'QSettings program'
SETTINGS_TRAY = 'settings/tray'


class MainWindow(QMainWindow):
    """
         Checkbox.
         Will initialize in the constructor.
    """
    check_box = None

    # Override the class constructor
    def __init__(self):
        # Be sure to call the super class method
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(480, 240))  # Set sizes
        self.setWindowTitle("Settings Application")  # Set a title
        central_widget = QWidget(self)  # Create a central widget
        self.setCentralWidget(central_widget)  # Set the central widget

        grid_layout = QGridLayout()  # Create a QGridLayout
        central_widget.setLayout(grid_layout)  # Set the layout into the central widget
        grid_layout.addWidget(QLabel("Application, which can minimize to Tray", self), 0, 0)

        # Add a checkbox, which will depend on the behavior of the program when the window is closed
        self.check_box = QCheckBox('Settings CheckBox for minimizing to tray')
        grid_layout.addWidget(self.check_box, 1, 0)
        # grid_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding), 2, 0)

        # The checkbox for the conversion tool
        self.converter_checkbox = QCheckBox('Convert')
        grid_layout.addWidget(self.converter_checkbox, 2, 0)
        self.converter_checkbox.setToolTip("Convert the output file")



        # Get settings
        settings = QSettings()
        # Get checkbox state with speciying type of checkbox:
        # type=bool is a replacement of toBool() in PyQt5
        check_state = settings.value('check_box',False, type=bool)
        check_converter = settings.value('converter_checkbox',False, type=bool)

        # Set state
        self.check_box.setChecked(check_state)
        self.converter_checkbox.setChecked(check_converter)

        # connect the slot to the signal by clicking the checkbox to save the state settings
        self.check_box.clicked.connect(self.save_check_box_settings)
        self.converter_checkbox.clicked.connect(self.save_converter_checkbox_settings)


    # Slot checkbox to save the settings
    def save_check_box_settings(self):
        settings = QSettings()
        settings.setValue('check_box', self.check_box.isChecked())
        settings.sync()


    # Slot checkbox to save the settings
    def save_converter_checkbox_settings(self):
        settings = QSettings()
        settings.setValue('converter_checkbox', self.converter_checkbox.isChecked())
        settings.sync()

if __name__ == "__main__":
    import sys

    # To ensure that every time you call QSettings not enter the data of your application,
    # which will be the settings, you can set them globally for all applications
    QCoreApplication.setApplicationName(ORGANIZATION_NAME)
    QCoreApplication.setOrganizationDomain(ORGANIZATION_DOMAIN)
    QCoreApplication.setApplicationName(APPLICATION_NAME)

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
