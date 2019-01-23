# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap
from ui_res.mainwindow import Ui_MainWindow
from epub_exporter import Ebook
from downloader_thread import DownloaderThread
from ui.choose_volume import choose_volume
from cover_downloader import download_cover
from requests.exceptions import RequestException
import update_window
is_win = sys.platform == 'win32'
if is_win:
    from PyQt5.QtWinExtras import QWinTaskbarButton


class AppWindow(QMainWindow):
    def __init__(self, argv):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.update_mode = False
        self.downloader_thread = None
        self.book = None
        self.cover = None
        self.title = None
        self.version = 1.1
        self.titles_of_chapter = list()
        self.full_chapters = dict()

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
        self.cover = None
        self.title = None
        self.change_update_mode(False)
        self.ui.actionNewBook.setDisabled(True)
        self.ui.actionSave_as.setDisabled(True)
        self.ui.actionSave.setDisabled(True)
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
        self.title, self.cover = self.book.load_from_file(path)

        self.ui.actionSave.setEnabled(True)
        self.ui.actionSave_as.setEnabled(True)
        self.ui.download_button.setEnabled(True)
        self.ui.actionNewBook.setEnabled(True)
        self.ui.novel_url.setText(self.book.source_url)

        self.log("File " + path + " sucesfully loaded")
        self.log(self.book.status())

        self.change_update_mode(True)

    def change_update_mode(self, mode):
        self.book_status_update()
        self.update_mode = mode
        if mode:
            self.ui.download_button.setText("Update")
            self.ui.download_button.clicked.disconnect()
            self.ui.download_button.clicked.connect(self.update_button_pressed)
        else:
            self.ui.download_button.setText("Download")
            self.ui.download_button.clicked.disconnect()
            self.ui.download_button.clicked.connect(self.download_button_pressed)

    def log(self, p_str):
        self.ui.log.append(p_str)

    def book_status_update(self):
        if self.book is None:
            self.ui.book_cover.setPixmap(QPixmap(":images/default_cover.png"))
            self.ui.book_info.setText("There is currently no book loaded")
            return

        cover = QPixmap()
        cover.loadFromData(self.cover)
        self.ui.book_cover.setPixmap(cover)

        self.ui.book_info.setText(self.book.status())

    def download_button_pressed(self):
        url = self.ui.novel_url.text()
        self.log("Downloading from "+url)

        try:
            self.title, self.cover, volumes_dict = download_cover(self.ui.novel_url.text())
        except RequestException:
            self.log("Connection error. Check if your Url is valid.")
            return
        except ValueError:
            self.log("Website parsing error. Check if your Url is valid.")
            return

        self.log("Downloading book " + self.title)

        for book_title, foo in volumes_dict.items():
            self.log(book_title)

        choosen_volume = choose_volume(volumes_dict)
        if choosen_volume is None:
            return
        self.titles_of_chapter, _ = zip(*volumes_dict[choosen_volume])

        self.log("downloading volume: " + choosen_volume)
        self.book = Ebook()
        self.book.source_url = self.ui.novel_url.text()
        self.book.init(self.title, choosen_volume, self.cover)

        self.book_status_update()

        self.ui.download_button.setDisabled(True)
        self.ui.stop_button.setEnabled(True)

        self.start_progress_bar(len(volumes_dict[choosen_volume]))

        self.downloader_threads = [DownloaderThread(chapter) for chapter in volumes_dict[choosen_volume]]
        for downloader_thread in self.downloader_threads:
            downloader_thread.new_chapter.connect(self.new_chapter_downloaded)
            downloader_thread.start()

    def update_button_pressed(self):
        url = self.ui.novel_url.text()
        self.log("Downloading from "+url)

        try:
            self.title, self.cover, volumes_dict = download_cover(self.ui.novel_url.text())
        except RequestException:
            self.log("Connection error. Check if your Url is valid.")
            return
        except ValueError:
            self.log("Website parsing error. Check if your Url is valid.")
            return

        self.log("Downloading " + self.title)

        choosen_volume = self.book.volume_name

        self.log("downloading volume: " + choosen_volume)

        self.ui.download_button.setDisabled(True)
        self.ui.stop_button.setEnabled(True)

        chapters = volumes_dict[choosen_volume]

        i = 0
        for chapter_title, chapter_url in chapters:
            i += 1
            if chapter_title == self.book.get_last_chapter_title():
                break
        chapters = chapters[i:]

        self.downloader_thread = DownloaderThread(chapters)
        self.downloader_thread.new_chapter.connect(self.new_chapter_downloaded)
        self.downloader_thread.end_of_download.connect(self.end_of_download)

        self.start_progress_bar(len(chapters))

        self.downloader_thread.start()

    def new_chapter_downloaded(self, title, text):
        self.full_chapters[title] = text
        self.increment_progress_bar()
        self.log(title)
        if set(self.titles_of_chapter) == set(self.full_chapters.keys()):
            self.end_of_download()

    def end_of_download(self):
        self.log("Download ended")

        for title in self.titles_of_chapter:
            self.book.add_chapter(title, self.full_chapters[title])
        self.titles_of_chapter = list()
        self.full_chapters = dict()

        self.ui.actionSave_as.setEnabled(True)
        self.ui.stop_button.setDisabled(True)
        self.ui.download_button.setEnabled(True)
        self.ui.actionNewBook.setEnabled(True)

        self.stop_progress_bar()
        self.log(self.book.status())
        self.change_update_mode(True)

    def stop_button_pressed(self):
        self.downloader_thread.end()

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


app = QApplication(sys.argv)
w = AppWindow(sys.argv)
w.show()
sys.exit(app.exec_())
