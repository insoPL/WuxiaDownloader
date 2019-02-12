# -*- coding: utf-8 -*-
from PyQt5.QtCore import QUrl, pyqtSignal, QThread
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest


class UpdateDownloaderThread(QThread):
    update_downloaded = pyqtSignal()
    connection_error = pyqtSignal(str)

    def __init__(self):
        url = 'https://gist.githubusercontent.com/insoPL/4afc2af9011b030381d2459711dfefc7/raw/e1cdc190264f8b93dc143e8bde6671887cbb161f/debug_version'
        self._url = QUrl(url)
        if not self._url.isValid():
            self.connection_error.emit("Url invalid")
            return
        self._network_manager = QNetworkAccessManager()
        self._reply = None

        QThread.__init__(self)

    def run(self):
        request = QNetworkRequest(self._url)
        self._reply = self._network_manager.get(request)
        self._reply.finished.connect(self.read_update)
        self.exec()

    def read_update(self):
        self._reply.finished.disconnect()
        if self._reply.error():
            err_msg = self._reply.errorString()
            self.connection_error.emit(err_msg)
            return
        if self._reply.isReadable():
            page_data = self._reply.readAll()
            try:
                self.new_version, self.update_url, self.update_log = _parse_update_log(page_data)
                self.update_downloaded.emit()
            except ValueError:
                self.connection_error.emit("Cover parsing error")
                return
        else:
            self.connection_error.emit("Reply unreadable")


def _parse_update_log(log):
    log = str(log)
    log = log[:-1]
    log = log[2:]
    update_log = log.split('\\n')
    new_version = update_log[0]
    update_url = update_log[1]
    update_log = "\n".join(update_log[2:])
    return float(new_version), update_url, update_log
