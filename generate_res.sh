rm -r generated_ui_res
mkdir generated_ui_res
pyuic5 --from-imports ui/mainwindow.ui > generated_ui_res/mainwindow.py
pyuic5 --from-imports ui/choose_volume_raw.ui > generated_ui_res/choose_volume_raw.py
pyrcc5 ui/resources.qrc > generated_ui_res/resources_rc.py
