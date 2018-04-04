# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
from epub_exporter import BookEpub


def download_and_parse(url):
    print("parsing " + str(i))
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    article = soup.find('div', class_='fr-view')

    content = list()
    for art in article.find_all('p'):
        foo = art.get_text()
        if len(foo) > 0:
            content.append(foo)

    text = ['<p>' + foo + '</p>' for foo in content[1:]]
    text = ''.join(text)

    title = content[0]

    return title, text


book = BookEpub()

for i in range(1048,1051):
    title, text = download_and_parse("https://www.wuxiaworld.com/novel/against-the-gods/atg-chapter-" + str(i))
    book.add_chapter(title, text)

book.save()
