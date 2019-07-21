# -*- coding: utf-8 -*-
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtNetwork import QNetworkAccessManager

from downloaders.universal_downloader import UniversalDownloaderThread


class UpdateDownloaderThread(QThread):
    download_finished = pyqtSignal()
    connection_error = pyqtSignal(str)

    def __init__(self):
        self._network_manager = QNetworkAccessManager()
        self.downloader = None
        QThread.__init__(self)

    def run(self):
        url = 'https://gist.githubusercontent.com/insoPL/4afc2af9011b030381d2459711dfefc7/raw'
        self.downloader = UniversalDownloaderThread(url, self._network_manager, parser)
        self.downloader.connection_error.connect(self.connection_error)
        self.downloader.download_finished.connect(self.download_finished)
        self.exec()

    def get_data(self):
        return self.downloader.get_data()


def parser(data):
    data = str(data)
    data = data[:-1]
    data = data[2:]
    data = data.split('\\n')
    new_version = data[0]
    update_url = data[1]
    update_log = "\n".join(data[2:])
    return float(new_version), update_url, update_log

