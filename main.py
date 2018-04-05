# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QLabel
from PyQt5.QtGui import QPixmap
from mainwindow import Ui_MainWindow
from epub_exporter import Ebook
from downloader_thread import DownloaderThread


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.update_mode=False

        self.setWindowTitle("Wuxia Downloader")

        self.ui.download_button.pressed.connect(self.download_button_pressed)
        self.ui.actionSave_as.triggered.connect(self.save_to_button_pressed)
        self.ui.actionopen_epub_file.triggered.connect(self.open_epub_button_pressed)
        self.ui.abort_button.pressed.connect(self.abort_button_pressed)
        self.ui.novel_url.setText("https://www.wuxiaworld.com/novel/against-the-gods")

        self.show()

    def open_epub_button_pressed(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setNameFilter("eBook Files (*.epub)")

        if dlg.exec_():
            self.ui.actionSave_as.setEnabled(True)
            path = dlg.selectedFiles()[0]
            self.book = Ebook()
            self.book.init_from_file(path)  # self book not init yet
            self.log("File "+path+" loaded")
            self.log(self.book.status())
            self.update_mode = True
            self.ui.download_button.setText("Update")
            self.book_status_update()

            self.last_chapter = self.book.book_content.get_metadata("wuxiadownloader","lastchapter")[0][0]

    def log(self, p_str):
        self.ui.log.append(p_str)

    def book_status_update(self):
        cover = QPixmap()
        bytecover = self.book.get_cover()
        cover.loadFromData(bytecover.content)
        self.ui.book_cover.setPixmap(cover)

        text = self.book.book_content.title
        text += '\n' + self.book.status()
        self.ui.book_info.setText(text)

    def download_button_pressed(self):
        url = self.ui.novel_url.text()
        self.progress_bar_counter=0
        self.log("Downloading from "+url)

        self.book = Ebook()

        self.ui.abort_button.setEnabled(True)
        self.ui.download_button.setDisabled(True)
        self.downloader_thread = DownloaderThread(self.ui.novel_url.text(), self.update_mode)
        self.downloader_thread.new_chapter.connect(self.new_chapter_downloaded)
        self.downloader_thread.end_of_download.connect(self.end_of_download)
        self.downloader_thread.cover_retrived.connect(self.cover_retrived)
        self.downloader_thread.start()

    def cover_retrived(self, title):
        self.book.init(title)
        self.log("Downloading "+self.book.book_content.title)
        self.ui.progress_bar.setMaximum(self.downloader_thread.limit)
        self.book_status_update()

    def new_chapter_downloaded(self, title, text):
        if self.update_mode and title in self.last_chapter:
            self.downloader_thread.running = False
            self.log("last chapter")
            return
        self.progress_bar_counter += 1
        self.ui.progress_bar.setValue(self.progress_bar_counter)
        self.log(title)
        self.book.add_chapter(title, text)

    def end_of_download(self):
        self.log("Download ended")
        self.ui.actionSave_as.setDisabled(False)
        self.ui.abort_button.setDisabled(True)
        self.ui.progress_bar.setValue(0)
        if self.update_mode:
            self.book.update_data()
        else:
            self.book.set_meta()
        self.log(self.book.status())
        self.book_status_update()

    def abort_button_pressed(self):
        self.downloader_thread.running = False

    def save_to_button_pressed(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setNameFilter("eBook Files (*.epub)")

        if dlg.exec_():
            path = dlg.selectedFiles()[0]

            if ".epub" not in path:
                path += ".epub"

            self.log("Saving file to "+path)
            self.book.save(path)


app = QApplication(sys.argv)
w = AppWindow()
w.show()
sys.exit(app.exec_())