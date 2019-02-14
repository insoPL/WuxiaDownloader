from PyQt5.QtCore import QUrl, pyqtSignal, QThread
from PyQt5.QtNetwork import QNetworkRequest, QNetworkAccessManager


class UnversalDownloaderThread(QThread):
    download_finished = pyqtSignal()
    connection_error = pyqtSignal(str)

    def __init__(self, url):
        self.qurl = QUrl(url)
        if not self.qurl.isValid():
            self.connection_error.emit("Url invalid")
            return

        self._network_manager = QNetworkAccessManager()
        self._reply = None
        _parsed_data = None

        QThread.__init__(self)

    def run(self):
        request = QNetworkRequest(self.qurl)
        self._reply = self._network_manager.get(request)
        self._reply.finished.connect(self.data_retrived)
        self.exec()

    def data_retrived(self):
        self._reply.finished.disconnect()
        if self._reply.error():
            err_msg = self._reply.errorString()
            self.connection_error.emit(err_msg)
            return
        if self._reply.isReadable():
            page_data = self._reply.readAll()
            try:
                self._parsed_data = self.parser(page_data)
            except ValueError:
                self.connection_error.emit("Cover parsing error")
                return
            self.download_finished.emit()
        else:
            self.connection_error.emit("Reply unreadable")

    def get_data(self):
        return self._parsed_data
