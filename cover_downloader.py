# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup


def download_cover(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    book_title = soup.find('h4')
    if book_title is None:
        raise ValueError
    book_title = book_title.get_text()

    cover_img_url = soup.find('img', class_='media-object')
    if cover_img_url is None:
        raise ValueError
    cover_img_url = cover_img_url.get("src")

    if "https://" not in cover_img_url:
        cover_img_url = "https://www.wuxiaworld.com"+cover_img_url

    response = requests.get(cover_img_url)
    cover_img = response.content

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
        chapter_url_list = [(chapter.getText().replace("\n", ""), chapter.a.get("href")) for chapter in
                            chapter_url_list]

        books[title] = chapter_url_list

    return book_title, cover_img, books
