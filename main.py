# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from mainwindow import Ui_MainWindow
from epub_exporter import BookEpub
from downloader_thread import DownloaderThread


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle("Wuxia Downloader")

        self.ui.download_button.pressed.connect(self.download)
        self.ui.actionSave_as.triggered.connect(self.save)
        self.ui.abort_button.pressed.connect(self.abort_button)
        self.ui.novel_url.setText("https://www.wuxiaworld.com/novel/against-the-gods")

        self.show()

    def log(self, p_str):
        self.ui.log.append(p_str)

    def download(self):
        url = self.ui.novel_url.text()
        self.progress_bar_counter=0
        self.log("Downloading from "+url)

        self.ui.abort_button.setEnabled(True)
        self.downloader_thread = DownloaderThread(self.ui.novel_url.text())
        self.downloader_thread.new_chapter.connect(self.new_chapter_downloaded)
        self.downloader_thread.end_of_download.connect(self.end_of_download)
        self.downloader_thread.cover_retrived.connect(self.cover_retrived)
        self.downloader_thread.start()

    def cover_retrived(self):
        self.log("Downloading "+self.downloader_thread.book_title)
        self.ui.progress_bar.setMaximum(self.downloader_thread.limit)
        self.book = BookEpub(self.downloader_thread.book_title)



    def new_chapter_downloaded(self, title, text):
        self.progress_bar_counter += 1
        self.ui.progress_bar.setValue(self.progress_bar_counter)
        self.log("Chapter: " + title)
        self.book.add_chapter(title, text)

    def end_of_download(self):
        self.log("Download ended")
        self.log(self.book.status())
        self.ui.actionSave_as.setDisabled(False)
        self.ui.abort_button.setDisabled(True)
        self.ui.progress_bar.setValue(0)

    def abort_button(self):
        self.downloader_thread.running = False

    def save(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setNameFilter("eBook Files (*.epub)")

        if dlg.exec_():
            path = dlg.selectedFiles()[0]
            self.log("Saving file to "+path)
            self.book.save(path)


app = QApplication(sys.argv)
w = AppWindow()
w.show()
sys.exit(app.exec_())