# -*- coding: utf-8 -*-
import gc
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap
from ui_res.mainwindow import Ui_MainWindow
from epub_exporter import Ebook
from downloader_thread import DownloaderThread
from ui.choose_volume import choose_volume
from cover_downloader import process_cover
from requests.exceptions import RequestException
import update_window
import logging
is_win = sys.platform == 'win32'
if is_win:
    from PyQt5.QtWinExtras import QWinTaskbarButton
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PyQt5.QtCore import QUrl

class AppWindow(QMainWindow):
    def __init__(self, argv):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.book = None
        self.downloader_thread = None
        self.version = 1.1

        self.setWindowTitle("WuxiaDownloader")

        self.ui.download_button.clicked.connect(self.download_button_pressed)
        self.ui.actionSave.triggered.connect(self.save_button_pressed)
        self.ui.actionSave_as.triggered.connect(self.save_to_button_pressed)
        self.ui.actionopen_epub_file.triggered.connect(self.open_epub_button_pressed)
        self.ui.stop_button.clicked.connect(self.stop_button_pressed)
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionNewBook.triggered.connect(self.new_book_pressed)
        self.ui.actionAbout.triggered.connect(self.show_about)
        self.ui.actionCheck_For_Updates.triggered.connect(self.check_for_updates)
        self.ui.novel_url.setText("https://www.wuxiaworld.com/novel/against-the-gods")

        self.ui.actionNewBook.setShortcut('Ctrl+N')
        self.ui.actionExit.setShortcut('Ctrl+E')
        self.ui.actionSave.setShortcut('Ctrl+S')
        self.ui.actionopen_epub_file.setShortcut('Ctrl+O')

        self.show()

        if is_win:
            button = QWinTaskbarButton(self)
            button.setWindow(self.windowHandle())
            self.icon_progress_bar = button.progress()

        if len(argv) > 1:
            path = argv[1]
            if path[-4:] == "epub":  # if path is a file that name ends with "epub"
                self.load_epub_from_file(path)

    def check_for_updates(self):
        update_window.check_for_updates(self.version)

    def start_progress_bar(self, maximum):
        if maximum < 1:
            return

        self.progress_bar_counter = 0

        if is_win:
            self.icon_progress_bar.setValue(0)
            self.icon_progress_bar.setVisible(True)
            self.icon_progress_bar.setMaximum(maximum)

        self.ui.progress_bar.setValue(0)
        self.ui.progress_bar.setEnabled(True)
        self.ui.progress_bar.setMaximum(maximum)

    def increment_progress_bar(self):
        self.progress_bar_counter += 1
        self.ui.progress_bar.setValue(self.progress_bar_counter)
        if is_win:
            self.icon_progress_bar.setValue(self.progress_bar_counter)

    def stop_progress_bar(self):
        self.ui.progress_bar.setValue(0)
        self.ui.progress_bar.setEnabled(False)
        if is_win:
            self.icon_progress_bar.setValue(0)
            self.icon_progress_bar.setVisible(False)

    def new_book_pressed(self):
        self.book = None
        self.ui.actionNewBook.setDisabled(True)
        self.ui.actionSave_as.setDisabled(True)
        self.ui.actionSave.setDisabled(True)
        self.book_status_update()
        self.log("Book deleted from memory")

    def open_epub_button_pressed(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setNameFilter("eBook Files (*.epub)")

        if dlg.exec_():
            path = dlg.selectedFiles()[0]
            self.load_epub_from_file(path)

    def load_epub_from_file(self, path):
        self.book = Ebook()
        self.book.load_from_file(path)

        self.ui.actionSave.setEnabled(True)
        self.ui.actionSave_as.setEnabled(True)
        self.ui.download_button.setEnabled(True)
        self.ui.actionNewBook.setEnabled(True)
        self.ui.novel_url.setText(self.book.source_url)

        self.log("File " + path + " sucesfully loaded")
        self.book_status_update()
        self.log(self.book.status())

    def log(self, p_str):
        logging.info(p_str)
        self.ui.log.append(p_str)

    def book_status_update(self):
        if self.book is None:
            self.ui.book_cover.setPixmap(QPixmap(":images/default_cover.png"))
            self.ui.book_info.setText("There is currently no book loaded")
            return

        cover = QPixmap()
        cover.loadFromData(self.book.cover)
        self.ui.book_cover.setPixmap(cover)

        self.ui.book_info.setText(self.book.status())

    def download_button_pressed(self):
        url = self.ui.novel_url.text()
        self.log("Downloading cover from "+url)
        self.raw_cover_network_manager = QNetworkAccessManager()
        self.raw_cover_reply = self.raw_cover_network_manager.get(QNetworkRequest(QUrl(url)))
        self.raw_cover_reply.finished.connect(self.cover_retrived)

    def cover_retrived(self):
        title, cover, volumes_dict = process_cover(self.raw_cover_reply.readAll())
        del self.raw_cover_network_manager
        del self.raw_cover_reply
        url = self.ui.novel_url.text()
        self.log("Downloading book " + title)

        if self.book is None:
            chosen_volume = choose_volume(volumes_dict)
            if chosen_volume is None:
                return
            self.log("downloading volume: " + chosen_volume)
            chapters = volumes_dict[chosen_volume]

            self.book = Ebook(title, chosen_volume, cover, url)
            self.book_status_update()
        else:
            chosen_volume = self.book.volume_name
            self.log("downloading volume: " + chosen_volume)
            chapters = [(a, b) for a, b in volumes_dict[chosen_volume] if a not in self.book.get_titles_of_chapters()]
            if len(chapters) == 0:
                self.log("Book is already up-to-date")
                return

        self.ui.download_button.setDisabled(True)
        self.ui.stop_button.setEnabled(True)

        self.start_progress_bar(len(chapters))

        self.downloader_thread = DownloaderThread(chapters)
        self.downloader_thread.new_chapter.connect(self.new_chapter_downloaded)
        self.downloader_thread.end_of_download.connect(self.end_of_download)
        self.downloader_thread.start()

    def new_chapter_downloaded(self, chapter_title):
        self.increment_progress_bar()
        self.log(chapter_title)

    def end_of_download(self):
        self.log("Download ended")

        list_of_titles, _ = zip(*self.downloader_thread.raw_list_of_chapters)
        for title in list_of_titles:
            self.book.add_chapter(title, self.downloader_thread.ready_chapters[title])
        del self.downloader_thread

        self.ui.actionSave_as.setEnabled(True)
        self.ui.stop_button.setDisabled(True)
        self.ui.download_button.setEnabled(True)
        self.ui.actionNewBook.setEnabled(True)

        self.stop_progress_bar()
        self.log(self.book.status())

    def stop_button_pressed(self):
        self.downloader_thread.cancel()
        del self.downloader_thread
        del self.book
        self.ui.download_button.setEnabled(True)
        self.ui.stop_button.setDisabled(True)
        self.stop_progress_bar()

        self.log("Download Canceled")

    def save_to_button_pressed(self):
        dlg = QFileDialog()
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        default_name = (self.book.title+" "+self.book.volume_name)
        dlg.selectFile(default_name)
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setNameFilter("eBook File (*.epub)")

        if dlg.exec_():
            path = dlg.selectedFiles()[0]

            if ".epub" not in path:
                path += ".epub"

            self.log("Saving file to "+path)
            try:
                self.book.save(path)
            except OSError:
                self.log("Saving error: No permissions")

    def save_button_pressed(self):
        if self.book.file_path is None:
            self.log("Save error")
            return

        path = self.book.file_path
        try:
            self.book.save(path)
        except OSError:
            self.log("Saving error: No permissions")
        self.log("Epub saved: "+path)

    def show_about(self):
        about_dialog = QMessageBox(self)
        about_dialog.setWindowTitle("About")
        about_dialog.setText(
            "<div style=\"text-align: center\">" +
            "<p>WuxiaDownloader "+str(self.version)+"</p>" +
            "<p>Created by InsoPL</p>" +
            "<p>Distributed Under MIT License</p>" +
            "<p>More info and source code avalible</p>" +
            "<p><a href=\"https://github.com/insoPL/WuxiaDownloader\" style=\"color: #cccccc\">https://github.com/insoPL/WuxiaDownloader</a></p>"+
            "</div>"
        )

        about_dialog.show()

    def dragEnterEvent(self, e):
        data = e.mimeData().text()
        if data[:4] == "file" and data[-4:] == "epub":  # if draged item is a file that name ends with "epub"
            e.acceptProposedAction()

    def dropEvent(self, e):
        path = e.mimeData().text()
        path = path[8:]
        self.load_epub_from_file(path)
        self.log(path)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info("Initializing application")
    app = QApplication(sys.argv)
    w = AppWindow(sys.argv)
    logging.info("App ready")
    w.show()
    sys.exit(app.exec_())
