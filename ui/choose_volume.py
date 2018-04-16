# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QDialog
from ui_res.choose_volume_raw import Ui_Dialog


def choose_volume(volumes_dict):
    volume_titles = [titles for titles, links in volumes_dict.items()]
    form = _ChooseBookWindow(volume_titles)
    form.exec()
    return form.item


class _ChooseBookWindow(QDialog):
    def __init__(self, titles):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.listWidget.addItems(titles)
        self.ui.dialogbutton.accepted.connect(self.ok_button_pressed)
        self.item=None

    def ok_button_pressed(self):
        self.item = self.ui.listWidget.currentItem().text()