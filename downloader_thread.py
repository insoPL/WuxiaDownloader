# -*- coding: utf-8 -*-
from PyQt5.QtCore import QThread, pyqtSignal
import requests
from bs4 import BeautifulSoup


class DownloaderThread(QThread):
    end_of_download = pyqtSignal()
    new_chapter = pyqtSignal(str, str)

    def __init__(self, list_of_chapters):  # list of tuples (title, url)
        self.running = True
        self.list_of_chapters = list_of_chapters
        QThread.__init__(self)

    def run(self):

        for chapter_title, chapter_url in self.list_of_chapters:
            try:
                text = _download_and_parse("https://www.wuxiaworld.com"+chapter_url)
            except EOFError:
                self.end_of_download.emit()
                return

            if "Teaser" in chapter_title:
                continue

            if not self.running:
                self.end_of_download.emit()
                return

            self.new_chapter.emit(chapter_title, text)

        self.end_of_download.emit()
        self.running = False

    def __del__(self):
        self.quit()
        self.wait()


def _download_and_parse(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    article = soup.find('div', class_='fr-view')
    if article is None:
        raise EOFError

    content = list()

    for art in article.find_all('p'):

        foo = art.get_text()
        if len(foo) > 0:
            content.append(foo)

    text = ['<p>' + foo + '</p>' for foo in content]
    text = ''.join(text)

    return text
