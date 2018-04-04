# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup


page = requests.get("https://www.wuxiaworld.com/novel/against-the-gods")
soup = BeautifulSoup(page.content, 'html.parser')

title = soup.find('h4')

print(title.get_text())
