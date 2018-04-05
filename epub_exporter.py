# -*- coding: utf-8 -*-
from ebooklib import epub
import os


class Ebook:
    def __init__(self):
        self.book_content = epub.EpubBook()
        self.chapters_in_queue = list()

    def init(self, title):
        self.book_content.set_identifier(title.lower().replace(" ", "-"))
        self.book_content.set_title(title)
        self.book_content.set_language('en')
        self.book_content.set_cover("image.png", open('cover.png', 'rb').read())

        if os.path.isfile("cover.png"):
            os.remove("cover.png")

    def init_from_file(self, path):
        self.book_content = epub.read_epub(path)

    def save(self, path):
        if os.path.isfile(path):
            os.remove(path)

        # write to the file
        epub.write_epub(path, self.book_content, {})

    def status(self):
        return "You have " + str(len(self.book_content.toc)) + " chapters loaded."

    def add_chapter(self, title, text):
        chapter = epub.EpubHtml(title=title, file_name=title.lower().replace(" ", "-")+ '.xhtml', lang='en')

        chapter.content = u'<h1>' + title + '</h1>'+text

        self.chapters_in_queue.append(chapter)

    def update_data(self):
        chapters = reversed(self.chapters_in_queue)
        for chapter in chapters:
            self.book_content.add_item(chapter)
            self.book_content.toc.append(chapter)
        self.book_content.spine = ['nav', *chapters]

        self.book_content.add_item(epub.EpubNcx())
        self.book_content.add_item(epub.EpubNav())

        self.chapters_in_queue = list()

    def set_meta(self):
        for chapter in self.chapters_in_queue:
            self.book_content.add_item(chapter)

        self.book_content.toc = self.chapters_in_queue

        # add default NCX and Nav file
        self.book_content.add_item(epub.EpubNcx())
        self.book_content.add_item(epub.EpubNav())

        # define CSS style
        style = 'BODY {color: white;}'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

        # add CSS file
        self.book_content.add_item(nav_css)

        # basic spine
        self.book_content.spine = ['nav', *self.chapters_in_queue]

        last = self.chapters_in_queue[-1]
        last = last.content[0:50]
        self.book_content.set_unique_metadata("wuxiadownloader", "lastchapter", last)

        self.chapters_in_queue = list()

    def get_cover(self):
        return self.get_item_of_type(epub.EpubCover)

    def get_item_of_type(self, type):
        for item in self.book_content.items:
            if isinstance(item, type):
                return item
        return None
