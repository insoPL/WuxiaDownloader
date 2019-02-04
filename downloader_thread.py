# -*- coding: utf-8 -*-
from PyQt5.QtCore import QUrl, pyqtSignal, QThread, pyqtSlot
from bs4 import BeautifulSoup
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest


class DownloaderThread(QThread):
    end_of_download = pyqtSignal()
    new_chapter = pyqtSignal(str)

    def __init__(self, list_of_chapters):  # list of tuples (title, url)
        self.raw_list_of_chapters = list_of_chapters
        self.network_manager = QNetworkAccessManager()
        self.replys = set()
        self.ready_chapters = dict()
        QThread.__init__(self)

    def run(self):
        list_of_titles, list_of_urls = zip(*self.raw_list_of_chapters)
        list_of_qurls = [QUrl("https://www.wuxiaworld.com"+chapter_url) for chapter_url in list_of_urls]
        for chapter_title, qurl in zip(list_of_titles, list_of_qurls):
            request = QNetworkRequest(qurl)
            reply = self.network_manager.get(request)
            assert isinstance(reply, QNetworkReply)
            chapter_reciver = self.generate_chapter_reciver(reply, chapter_title)
            reply.finished.connect(chapter_reciver)
            self.replys.add(reply)
        self.exec()

    def generate_chapter_reciver(self, reply, chapter_title):
        @pyqtSlot()
        def chapter_reciver():
            reply.finished.disconnect()
            self.replys.remove(reply)
            if reply.isReadable():
                site = reply.readAll()
                text = parse(site)
                self.ready_chapters[chapter_title] = text
                self.new_chapter.emit(chapter_title)
                if len(self.replys) == 0:
                    self.end_of_download.emit()
        return chapter_reciver

    def cancel(self):
        for reply in self.replys:
            reply.abort()
        self.quit()

    def __del__(self):
        self.wait()


def parse(page):
    if len(page) == 0:
        return ""

    soup = BeautifulSoup(page, 'html.parser')

    article = soup.find('div', class_='fr-view')
    if article is None:
        raise ValueError

    content = list()

    all_verses = article.find_all('p')

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
