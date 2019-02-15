# -*- coding: utf-8 -*-
import logging
import sys

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox

from downloaders.cover_downloader import CoverDownloaderThread
from downloaders.downloader_thread import DownloaderThread
from epub_exporter import Ebook
from ui.choose_volume import choose_volume
from ui.mainwindow import Ui_MainWindow
from downloaders.update_downloader import UpdateDownloaderThread
from update_window import UpdateWindow


class AppWindow(QMainWindow):
    def __init__(self, argv):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.book = None
        self.downloader_thread = None
        self.version = 1.0

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

        self.progress_bar = self.ui.downloadprogressbar

        self.show()

        if len(argv) > 1:
            path = argv[1]
            if path[-4:] == "epub":  # if path is a file that name ends with "epub"
                self.load_epub_from_file(path)

    def check_for_updates(self):
        self.downloader_thread = UpdateDownloaderThread()
        self.downloader_thread.download_finished.connect(self.update_retrived)
        self.downloader_thread.connection_error.connect(self.cover_retrived)
        self.downloader_thread.start()

    def update_retrived(self):
        self.downloader_thread.download_finished.disconnect()
        self.downloader_thread.connection_error.disconnect()
        new_version, update_url, update_log = self.downloader_thread.get_data()
        self.downloader_thread = None

        if self.version < new_version:
            update_window = UpdateWindow(self.version, new_version, update_url, update_log)
            update_window.exec()
        else:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("WuxiaDownloader " + str(self.version))
            msg_box.setText("Program is updated")
            msg_box.exec_()
        return True

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
        self.ui.download_button.setDisabled(True)
        url = self.ui.novel_url.text()
        self.log("Downloading cover from "+url)
        self.downloader_thread = CoverDownloaderThread(url)
        self.downloader_thread.cover_download_end.connect(self.cover_retrived)
        self.downloader_thread.connection_error.connect(self.network_error)
        self.downloader_thread.start()

    def cover_retrived(self):
        self.downloader_thread.cover_download_end.disconnect()
        book_title, cover_img, volumes_dict = self.downloader_thread.get_data()
        self.downloader_thread = None
        url = self.ui.novel_url.text()
        self.log("Downloading book " + book_title)

        if self.book is None:
            chosen_volume = choose_volume(volumes_dict)
            if chosen_volume is None:
                self.ui.download_button.setEnabled(True)
                return
            self.log("downloading volume: " + chosen_volume)
            chapters = volumes_dict[chosen_volume]

            self.book = Ebook(book_title, chosen_volume, cover_img, url)
            self.book_status_update()
        else:
            chosen_volume = self.book.volume_name
            self.log("downloading volume: " + chosen_volume)
            chapters = [(a, b) for a, b in volumes_dict[chosen_volume] if a not in self.book.get_titles_of_chapters()]
            if len(chapters) == 0:
                self.ui.download_button.setEnabled(True)
                self.log("Book is already up-to-date")
                return

        self.ui.stop_button.setEnabled(True)

        self.progress_bar.start(len(chapters))

        self.downloader_thread = DownloaderThread(chapters)
        self.downloader_thread.new_chapter.connect(self.new_chapter_downloaded)
        self.downloader_thread.connection_error.connect(self.network_error)
        self.downloader_thread.end_of_download.connect(self.end_of_download)
        self.downloader_thread.start()

    def new_chapter_downloaded(self, chapter_title):
        self.progress_bar.increment_progress_bar()
        self.log(chapter_title)

    def end_of_download(self):
        self.log("Download ended")

        chapters = self.downloader_thread.get_chapters()
        self.book.add_chapters(chapters)
        self.downloader_thread = None

        self.ui.actionSave_as.setEnabled(True)
        self.ui.stop_button.setDisabled(True)
        self.ui.download_button.setEnabled(True)
        self.ui.actionNewBook.setEnabled(True)

        self.progress_bar.stop()
        self.log(self.book.status())

    def stop_button_pressed(self):
        self.downloader_thread.new_chapter.disconnect()
        self.downloader_thread.end_of_download.disconnect()
        self.downloader_thread.cancel()
        self.downloader_thread = None
        self.book = None
        self.book_status_update()
        self.ui.download_button.setEnabled(True)
        self.ui.stop_button.setDisabled(True)
        self.progress_bar.stop()

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

    def network_error(self, msg):
        if isinstance(self.downloader_thread, DownloaderThread):
            self.downloader_thread.new_chapter.disconnect()
            self.downloader_thread.end_of_download.disconnect()
            self.downloader_thread.connection_error.disconnect()
            self.progress_bar.stop()
        elif isinstance(self.downloader_thread, CoverDownloaderThread):
            self.downloader_thread.cover_download_end.disconnect()
            self.downloader_thread.connection_error.disconnect()

        error_dialog = QMessageBox(self)
        error_dialog.setWindowTitle("Connection Error")
        error_dialog.setText(
            "<div style=\"text-align: center\">" +
            "<p>Connection Error</p>" +
            "<p>"+msg+"</p>" +
            "<p>Please check if your url is valid</p>" +
            "<p>and your internet connection</p>" +
            "</div>"
        )
        error_dialog.show()

        self.downloader_thread = None
        self.book = None
        self.book_status_update()
        self.ui.download_button.setEnabled(True)
        self.ui.stop_button.setDisabled(True)

        self.log("Download Error: "+msg)

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
