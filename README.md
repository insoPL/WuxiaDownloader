# WuxiaDownloader

Small program created to download wuxia novels from wuxiaworld and save them as handy epub files.
When your favorite wuxia is updated you can easliy update your epub by opening file("File>Open epub file" or drag&drop)
and clicking "update" button.

![Screen](https://www.dropbox.com/s/11ukdjhb4vginjw/WuxiaDownloader.PNG?raw=1)

## Dependencies

For program to compile you need following libraries:
* [PyQt5](https://www.riverbankcomputing.com/software/pyqt)
* [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)
* [ebooklib](https://github.com/aerkalov/ebooklib)
* [Reqests](http://docs.python-requests.org/en/master/)

## Compiling

Before running program you need to compile resource and ui files using pyuic:

```
pyuic5 --from-imports ui\mainwindow.ui > ui_res\mainwindow.py
pyuic5 --from-imports ui\choose_volume_raw.ui > ui_res\choose_volume_raw.py
pyrcc5 ui\resources.qrc > ui_res\resources_rc.py
```

## Creating single executable file

Executable files can be created using pyinstaller
There is pyinstaller's .spec file in main catalogue ("WuxiaDownloader.spec") configured to export program to single executable file.
It was tested on:
* MacOS
* Windows 10
* Ubuntu 16.04

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
