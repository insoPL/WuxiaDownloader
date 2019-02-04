mkdir ui_res
pyuic5 --from-imports ui/mainwindow.ui > ui/mainwindow.py
pyuic5 --from-imports ui/choose_volume_raw.ui > ui/choose_volume_raw.py
pyrcc5 ui/resources.qrc > ui/resources_rc.py
