# -*- coding: utf-8 -*-
import logging
from PyQt5.QtCore import QThread, pyqtSignal
import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup


class DownloaderThread(QThread):
    end_of_download = pyqtSignal(str)
    new_chapter = pyqtSignal(str, str)

    def __init__(self, list_of_chapters):  # list of tuples (title, url)
        self.running = True
        self.list_of_chapters = list_of_chapters
        QThread.__init__(self)

    def run(self):
        for chapter_title, chapter_url in self.list_of_chapters:
            try:
                text = _download_and_parse("https://www.wuxiaworld.com"+chapter_url)
            except RequestException:
                logging.error("RequestException while downloading chapters")
                self.end_of_download.emit("RequestException")
                return
            except ValueError:
                logging.error("Parsing Error")
                self.end_of_download.emit("Parsing Error")
                return
            if not self.running:
                self.end_of_download.emit("Stoped")
                return
            self.new_chapter.emit(chapter_title, text)
        self.end_of_download.emit("end")

    def __del__(self):
        self.quit()
        self.wait()

    def end(self):
        self.running = False


def _download_and_parse(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

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
