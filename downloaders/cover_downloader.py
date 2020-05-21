# -*- coding: utf-8 -*-
from PyQt5.QtCore import QUrl, pyqtSignal, QThread
from PyQt5.QtNetwork import QNetworkAccessManager
from bs4 import BeautifulSoup

from downloaders.universal_downloader import UniversalDownloaderThread


class CoverDownloaderThread(QThread):
    cover_download_end = pyqtSignal()
    connection_error = pyqtSignal(str)

    def __init__(self, url):  # list of tuples (title, url)
        self._url = url
        self._network_manager = QNetworkAccessManager()
        self.downloader = None

        QThread.__init__(self)

    def run(self):
        self.downloader = UniversalDownloaderThread(self._url, self._network_manager, _process_cover)
        self.downloader.connection_error.connect(self.connection_error)
        self.downloader.download_finished.connect(self.read_cover)
        self.exec()

    def read_cover(self):
        self.book_title, cover_img_url, self.books = self.downloader.get_data()
        self.downloader = UniversalDownloaderThread(cover_img_url, self._network_manager)
        self.downloader.download_finished.connect(self.cover_download_end)
        self.downloader.connection_error.connect(self.connection_error)

    def get_data(self):
        cover_img = self.downloader.get_data()
        return self.book_title, cover_img, self.books


def _process_cover(page):
    soup = BeautifulSoup(page.data(), 'html.parser')

    book_title = soup.find('h2')
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
        chapter_url_list = [(chapter.getText().replace("\n", "").strip(), chapter.a.get("href")) for chapter in
                            chapter_url_list]

        books[title] = chapter_url_list

    return book_title, cover_img_url, books
