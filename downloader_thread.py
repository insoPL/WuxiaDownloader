# -*- coding: utf-8 -*-
from PyQt5.QtCore import QThread, pyqtSignal
import requests
from bs4 import BeautifulSoup


class DownloaderThread(QThread):
    end_of_download = pyqtSignal()
    new_chapter = pyqtSignal(str, str, int)

    def __init__(self, url, limit):
        self.base_url = url
        self.limit = limit
        self.running = True
        QThread.__init__(self)

    def run(self):
        for i in range(self.limit):
            try:
                name, text = _download_and_parse(self.base_url+str(i))
            except EOFError:
                self.end_of_download.emit()
                return
            self.new_chapter.emit(name, text, i)
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
