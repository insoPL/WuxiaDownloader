# -*- coding: utf-8 -*-
from PyQt5.QtCore import QThread, pyqtSignal
import requests
from bs4 import BeautifulSoup


class DownloaderThread(QThread):
    end_of_download = pyqtSignal()
    new_chapter = pyqtSignal(str, str)
    cover_retrived = pyqtSignal()

    def __init__(self, url):
        self.base_url = url
        self.running = True
        QThread.__init__(self)

    def run(self):
        page = requests.get(self.base_url)
        soup = BeautifulSoup(page.content, 'html.parser')

        self.book_title = soup.find('h4').get_text()

        chapter_url_list = soup.find_all('li', class_='chapter-item')

        chapter_url_list = [chapter.a.get("href") for chapter in chapter_url_list]

        self.limit = len(chapter_url_list)

        self.cover_retrived.emit()

        for chapter_url in chapter_url_list:
            try:
                name, text = _download_and_parse("https://www.wuxiaworld.com"+chapter_url)
            except EOFError:
                self.end_of_download.emit()
                return
            self.new_chapter.emit(name, text)

            if not self.running:
                self.end_of_download.emit()
                return
        self.end_of_download.emit()
        self.running=False

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

    text = ['<p>' + foo + '</p>' for foo in content[1:]]
    text = ''.join(text)

    title = content[0]

    return title, text
