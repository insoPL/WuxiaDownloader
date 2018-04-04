# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from epub_exporter import BookEpub

book = BookEpub()

for i in range(1):
    page = requests.get("https://www.wuxiaworld.com/novel/against-the-gods/atg-chapter-800")
    soup = BeautifulSoup(page.content, 'html.parser')

    content = list()
    for item in soup.find_all('p', dir='ltr'):
        content.append(item.get_text())

    book.add_chapter(*content)

book.save()
