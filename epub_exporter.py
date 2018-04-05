# -*- coding: utf-8 -*-
from ebooklib import epub
import os


class Ebook:
    def __init__(self):
        self._book_content = epub.EpubBook()
        self.chapters = list()

    def init(self, title, cover):
        self.title = title
        self.cover = cover

    def load_from_file(self, path):
        loaded_articles = epub.read_epub(path)

        items = list(self.get_items_of_type(epub.EpubHtml, loaded_articles))
        items = items[1:]  # remove cover

        epub_cover = self.get_items_of_type(epub.EpubCover, loaded_articles)[0]
        self.cover = epub_cover.content
        self.title = loaded_articles.title
        self.chapters = items

    def save(self, path):
        if os.path.isfile(path):
            os.remove(path)

        self.set_meta()

        # write to the file
        epub.write_epub(path, self._book_content, {})

    def status(self):
        return "You have " + str(len(self.chapters)) + " chapters loaded."

    def add_chapter(self, title, text):
        chapter = epub.EpubHtml(title=title, file_name=title.lower().replace(" ", "-")+ '.xhtml', lang='en')

        chapter.content = u'<h1>' + title + '</h1>'+text

        self.chapters.append(chapter)

    def set_meta(self):
        self._book_content.set_identifier(self.title.lower().replace(" ", "-"))
        self._book_content.set_title(self.title)
        self._book_content.set_language('en')
        self._book_content.set_cover("image.png", self.cover)

        for chapter in self.chapters:
            self._book_content.add_item(chapter)

        self._book_content.toc = self.chapters

        # add default NCX and Nav file
        self._book_content.add_item(epub.EpubNcx())
        self._book_content.add_item(epub.EpubNav())

        # define CSS style
        style = 'BODY {color: white;}'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)

        # add CSS file
        self._book_content.add_item(nav_css)

        # basic spine
        self._book_content.spine = ['nav', *self.chapters]

        # last = self.chapterse[-1]
        # last = last.content[0:50]
        # self._book_content.set_unique_metadata("wuxiadownloader", "lastchapter", last)
        #
        # self.chapters_in_queue = list()

    def get_items_of_type(self, typ, containter=None):
        ret_list = list()

        if containter is None:
            containter = self._book_content

        for item in containter.items:
            if type(item) is typ:
                ret_list.append(item)
        return ret_list
