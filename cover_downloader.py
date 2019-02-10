# -*- coding: utf-8 -*-
from PyQt5.QtCore import QUrl, pyqtSignal, QThread
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest
from bs4 import BeautifulSoup


class CoverDownloaderThread(QThread):
    cover_download_end = pyqtSignal()
    connection_error = pyqtSignal(str)

    def __init__(self, url):  # list of tuples (title, url)
        self._network_manager = QNetworkAccessManager()
        self._url = QUrl(url)
        self._reply = None

        self.book_title = None
        self.books = None
        self.cover_img = None

        QThread.__init__(self)

    def run(self):
        request = QNetworkRequest(self._url)
        self._reply = self._network_manager.get(request)
        self._reply.finished.connect(self.read_cover)
        self.exec()

    def read_cover(self):
        self._reply.finished.disconnect()
        page_data = self._reply.readAll()
        self.book_title, cover_img_url, self.books = _process_cover(page_data)
        request = QNetworkRequest(cover_img_url)
        self._reply = self._network_manager.get(request)
        self._reply.finished.connect(self.get_cover_img)

    def get_cover_img(self):
        self._reply.finished.disconnect()
        self.cover_img = self._reply.readAll()
        self.cover_download_end.emit()


def _process_cover(page):
    soup = BeautifulSoup(page, 'html.parser')

    book_title = soup.find('h4')
    if book_title is None:
        raise ValueError
    book_title = book_title.get_text()

    cover_img_url = soup.find('img', class_='media-object')
    if cover_img_url is None:
        raise ValueError
    cover_img_url = cover_img_url.get("src")

    if "https://" not in cover_img_url:
        cover_img_url = "https://www.wuxiaworld.com"+cover_img_url

    cover_img_url = QUrl(cover_img_url)

    panels = soup.find_all("div", class_="panel panel-default")
    if panels is None:
        raise ValueError

    books = dict()
    for book in panels:
        title = book.find(class_="title")
        if title is None:  # panel is not a book
            continue
        title = title.get_text().replace("\n", "")

        chapter_url_list = book.find_all('li', class_='chapter-item')
        chapter_url_list = [(chapter.getText().replace("\n", ""), chapter.a.get("href")) for chapter in
                            chapter_url_list]

        books[title] = chapter_url_list

    return book_title, cover_img_url, books
