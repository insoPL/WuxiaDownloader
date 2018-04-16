pyuic5 --from-imports ui\mainwindow.ui > ui_res\mainwindow.py
pyuic5 --from-imports ui\choose_volume_raw.ui > ui_res\choose_volume_raw.py
pyrcc5 ui\resources.qrc > ui_res\resources_rc.py
