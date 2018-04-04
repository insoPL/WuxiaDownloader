# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication
from mainwindow import Ui_MainWindow


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Wuxia Downloader")

        self.ui.download_button.pressed.connect(self.download)

        self.show()

    def log(self, p_str):
        self.ui.log.append(p_str)

    def download(self):
        self.log("download")

app = QApplication(sys.argv)
w = AppWindow()
w.show()
sys.exit(app.exec_())