from PyQt5.QtCore import QUrl, pyqtSignal, QObject
from PyQt5.QtNetwork import QNetworkRequest


def empty_parser(page):
    return page


class UnversalDownloaderThread(QObject):
    download_finished = pyqtSignal()
    connection_error = pyqtSignal(str)

    def __init__(self, url, network_manager, parser=empty_parser):
        QObject.__init__(self)
        self._parsed_data = None
        self._parser = parser

        qurl = QUrl(url)
        if not qurl.isValid():
            self.connection_error.emit("Url invalid")
            return
        request = QNetworkRequest(qurl)
        self._reply = network_manager.get(request)
        self._reply.finished.connect(self._data_retrived)

    def _data_retrived(self):
        self._reply.finished.disconnect()
        if self._reply.error():
            err_msg = self._reply.errorString()
            self.connection_error.emit(err_msg)
            return
        if self._reply.isReadable():
            page_data = self._reply.readAll()
            try:
                self._parsed_data = self._parser(page_data)
            except ValueError:
                self.connection_error.emit("Cover parsing error")
                return
            self.download_finished.emit()
        else:
            self.connection_error.emit("Reply unreadable")

    def get_data(self):
        return self._parsed_data
