# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QVBoxLayout, QDialog, QLineEdit, QHBoxLayout, QPushButton, QProgressDialog, QLabel, QMessageBox
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtCore import pyqtSignal, Qt, QUrl

import requests


def check_for_updates(current_version):
    url = 'https://www.dropbox.com/s/51racakjuzc6nd0/version.txt?dl=1'
    page = requests.get(url)
    if not page: return False
    update_log = page.text

    new_version, update_url, update_log = _parse_update_log(update_log)

    if current_version < new_version:
        update_window = _UpdateWindow(current_version, new_version, update_url, update_log)
        update_window.exec()
    else:
        msg_box = QMessageBox()
        msg_box.setWindowTitle("WuxiaDownloader "+str(current_version))
        msg_box.setText("Program is updated")
        msg_box.exec_()

    return True


def _parse_update_log(log):
    update_log = log.split()
    new_version = update_log[0]
    update_url = update_log[1]
    update_log = "\n".join(update_log[2:])
    return float(new_version), update_url, update_log


class _UpdateWindow(QDialog):
    def __init__(self, current_version, new_version, update_url, update_log):
        super().__init__()
        self.update_url = update_url

        self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)
        self.setWindowIcon(QIcon(':/ui/images/icon.png'))
        self.setWindowTitle("Wuxiaworld Version "+str(current_version))
        self.resize(400, 300)

        grid = QVBoxLayout()
        grid.addWidget(QLabel("New version available Wuxiaworld Version "+str(new_version)))
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
