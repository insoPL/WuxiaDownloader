# -*- coding: utf-8 -*-
from ebooklib import epub


class BookEpub:
    def __init__(self):
        self.book_content = epub.EpubBook()
        self.chapters = list()
    
        # set metadata
        self.book_content.set_identifier('against-the-gods')
        self.book_content.set_title('Against The Gods')
        self.book_content.set_language('en')
    
        self.book_content.add_author('Mars Gravity')
        self.book_content.add_author('Alyschu', uid='Translator')

    def save(self):
        for chapter in self.chapters:
            self.book_content.add_item(chapter)

        self.book_content.toc = self.chapters

        # add default NCX and Nav file
        self.book_content.add_item(epub.EpubNcx())
        self.book_content.add_item(epub.EpubNav())
    
        # define CSS style
        style = 'BODY {color: white;}'
        nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    
        # add CSS file
        self.book_content.add_item(nav_css)
    
        # basic spine
        self.book_content.spine = ['nav', *self.chapters]
    
        # write to the file
        epub.write_epub('AgainstTheGods.epub', self.book_content, {})
    
    def add_chapter(self, name, *texts):
        # create chapter
        chapter = epub.EpubHtml(title=name, file_name='chapter_'+str(len(self.chapters)+1)+'.xhtml', lang='en')

        content = ''
        for text in texts:
            content += '<p>'+text+'</p>'

        chapter.content = u'<h1>'+name+'</h1>'+content
    
        # add chapter
        self.chapters.append(chapter)
