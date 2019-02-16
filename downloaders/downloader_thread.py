# -*- coding: utf-8 -*-
from PyQt5.QtCore import QUrl, pyqtSignal, QThread
from PyQt5.QtNetwork import QNetworkAccessManager
from bs4 import BeautifulSoup

from downloaders.universal_downloader import UniversalDownloaderThread


class DownloaderThread(QThread):
    end_of_download = pyqtSignal()
    new_chapter = pyqtSignal()
    connection_error = pyqtSignal(str)

    def __init__(self, list_of_chapters):  # list of tuples (title, url)
        self.list_of_chapter_titles, self.list_of_urls = zip(*list_of_chapters)
        self._network_manager = QNetworkAccessManager()
        self.list_of_universal_downloaders = list()
        self.counter = 0
        QThread.__init__(self)

    def run(self):
        list_of_qurls = [QUrl("https://www.wuxiaworld.com"+chapter_url) for chapter_url in self.list_of_urls]
        for chapter_title, qurl in zip(self.list_of_chapter_titles, list_of_qurls):
            downloader = UniversalDownloaderThread(qurl, self._network_manager, _parse_chapter)
            downloader.connection_error.connect(self.connection_error)
            downloader.download_finished.connect(self.chapter_reciver)
            self.list_of_universal_downloaders.append(downloader)
        self.exec()

    def chapter_reciver(self):
        self.new_chapter.emit()
        self.counter += 1
        if self.counter == len(self.list_of_universal_downloaders):
            self.end_of_download.emit()

    def get_data(self):
        chapters = list()
        for downloader in self.list_of_universal_downloaders:
            chapters.append(downloader.get_data())
        return zip(self.list_of_chapter_titles, chapters)

    def cancel(self):
        for reply in self.list_of_universal_downloaders:
            reply.abort()
        self.quit()

    def __del__(self):
        self.wait()


def _parse_chapter(page):
    if len(page) == 0:
        raise ValueError

    soup = BeautifulSoup(page, 'html.parser')

    article = soup.find('div', class_='fr-view')
    if article is None:
        raise ValueError

    content = list()

    all_verses = article.find_all('p')
    if all_verses is None:
        raise ValueError

    if "chapter" in all_verses[0].text.lower():  # if first verse contains word "chapter" delete it
        all_verses = all_verses[1:]

    for art in all_verses:
        foo = art.get_text()
        if len(foo) < 1:
            continue
        if "chapter" in foo.lower():
            continue
        content.append(foo)

    text = ['<p>' + foo + '</p>' for foo in content]
    text = ''.join(text)

    return text
