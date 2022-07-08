import os, sys, re
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import Qt
import qdarkstyle

class WeatherGUI(QMainWindow):
    def __init__(self):
        super(WeatherGUI, self).__init__()
        title = "Weather"
        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
        self.setWindowTitle(title)
        self.show()

def main() -> None:
    app = QApplication(sys.argv)
    window = WeatherGUI()
    sys.exit(app.exec_())

main()