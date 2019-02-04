from PyQt5 import QtWidgets
import sys
is_win = sys.platform == 'win32'
if is_win:
    from PyQt5.QtWinExtras import QWinTaskbarButton


class DownloadProgressBar(QtWidgets.QProgressBar):
    def __init__(self, parent):
        super(DownloadProgressBar, self).__init__(parent)
        self.progress_bar_counter = 0
        self.icon_progress_bar = None

    def start(self, maximum):
        if maximum < 1:
            return

        self.progress_bar_counter = 0

        self.setValue(0)
        self.setEnabled(True)
        self.setMaximum(maximum)

        if is_win:
            main_window = self.parentWidget().parentWidget()
            button = QWinTaskbarButton(main_window)
            button.setWindow(main_window.windowHandle())
            self.icon_progress_bar = button.progress()
            self.icon_progress_bar.setValue(0)
            self.icon_progress_bar.setVisible(True)
            self.icon_progress_bar.setMaximum(maximum)

    def increment_progress_bar(self):
        self.progress_bar_counter += 1
        self.setValue(self.progress_bar_counter)
        if is_win:
            self.icon_progress_bar.setValue(self.progress_bar_counter)

    def stop(self):
        self.setValue(0)
        self.setEnabled(False)
        if is_win:
            self.icon_progress_bar.setValue(0)
            self.icon_progress_bar.setVisible(False)
