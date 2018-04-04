# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup


page = requests.get("https://www.wuxiaworld.com/novel/against-the-gods")
soup = BeautifulSoup(page.content, 'html.parser')

chapter_list = soup.find_all('li', class_='chapter-item')

chapter_list = [chapter.a.get("href") for chapter in chapter_list]
print(chapter_list)
