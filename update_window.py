# -*- coding: utf-8 -*-
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QHBoxLayout, QPushButton, QLabel


class UpdateWindow(QDialog):
    def __init__(self, current_version, new_version, update_url, update_log):
        super().__init__()
        self.update_url = update_url

        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(QIcon(':/ui/images/icon.png'))
        self.setWindowTitle("Wuxiaworld Version " + str(current_version))
        self.resize(400, 300)

        grid = QVBoxLayout()
        grid.addWidget(QLabel("New version available Wuxiaworld Version " + str(new_version) + "\n"))
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
        url = QUrl(self.update_url)
        QDesktopServices.openUrl(url)
        self.close()
