# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QLineEdit, QHBoxLayout, QPushButton, QProgressDialog, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, Qt


def check_for_updates():
    update_log = """Features:
-sdasdasd
-sadadasd
-dsadsadsad
-sadasdasds"""

    new_version = "1.1"
    old_version = "1.0"

    update_window = _UpdateWindow(new_version, old_version, update_log)
    update_window.exec()


class _UpdateWindow(QDialog):
    def __init__(self, new_version, old_version, update_log):
        super().__init__()

        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(QIcon(':/ui/images/icon.png'))
        self.setWindowTitle("Wuxiaworld Version "+old_version)
        self.resize(400, 300)

        grid = QVBoxLayout()
        grid.addWidget(QLabel("New version available Wuxiaworld Version "+new_version))
        grid.addWidget(QLabel(update_log))
        grid.addStretch(1)
        grid.addLayout(self.cancel_accept_buttons())

        self.setLayout(grid)

    def cancel_accept_buttons(self):
        ok_button = QPushButton("Ok")
        download_button = QPushButton("Download New Version")

        ok_button.clicked.connect(self.close)
        download_button.clicked.connect(self.download_update)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(download_button)
        hbox.addWidget(ok_button)
        return hbox

    def download_update(self):
        raise NotImplemented
