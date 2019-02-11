# -*- coding: utf-8 -*-
from PyQt5.QtCore import QUrl, pyqtSignal, QThread, pyqtSlot
from bs4 import BeautifulSoup
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest


class DownloaderThread(QThread):
    end_of_download = pyqtSignal()
    new_chapter = pyqtSignal(str)
    connection_error = pyqtSignal(str)

    def __init__(self, list_of_chapters):  # list of tuples (title, url)
        self._raw_list_of_chapters = list_of_chapters
        self._network_manager = QNetworkAccessManager()
        self._replys = set()
        self._ready_chapters = dict()
        QThread.__init__(self)

    def run(self):
        list_of_titles, list_of_urls = zip(*self._raw_list_of_chapters)
        list_of_qurls = [QUrl("https://www.wuxiaworld.com"+chapter_url) for chapter_url in list_of_urls]
        for chapter_title, qurl in zip(list_of_titles, list_of_qurls):
            request = QNetworkRequest(qurl)
            reply = self._network_manager.get(request)
            assert isinstance(reply, QNetworkReply)
            chapter_reciver = self._generate_chapter_reciver(reply, chapter_title)
            reply.finished.connect(chapter_reciver)
            self._replys.add(reply)
        self.exec()

    def _generate_chapter_reciver(self, reply, chapter_title):
        @pyqtSlot()
        def chapter_reciver():
            reply.finished.disconnect()
            self._replys.remove(reply)
            if reply.error():
                err_msg = reply.errorString()
                self.connection_error.emit(err_msg)
                return
            if reply.isReadable():
                site = reply.readAll()
                try:
                    text = _parse_chapter(site)
                except ValueError:
                    self.connection_error.emit("Chapter parsing error")
                    return
                self._ready_chapters[chapter_title] = text
                self.new_chapter.emit(chapter_title)
                if len(self._replys) == 0:
                    self.end_of_download.emit()
            else:
                self.connection_error.emit("Reply unreadable")
        return chapter_reciver

    def get_chapters(self):
        ret_list = list()
        list_of_titles, _ = zip(*self._raw_list_of_chapters)
        for title in list_of_titles:
            packed_chapter = (title, self._ready_chapters[title])
            ret_list.append(packed_chapter)
        return ret_list

    def cancel(self):
        for reply in self._replys:
            reply.abort()
        self.quit()

    def __del__(self):
        self.wait()


def _parse_chapter(page):
    if len(page) == 0:
        return ""

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
