# -*- coding: utf-8 -*-
from downloaders.universal_downloader import UnversalDownloaderThread


class UpdateDownloaderThread(UnversalDownloaderThread):
    def __init__(self):
        url = 'https://gist.githubusercontent.com/insoPL/4afc2af9011b030381d2459711dfefc7/raw/e1cdc190264f8b93dc143e8bde6671887cbb161f/debug_version'
        UnversalDownloaderThread.__init__(self, url)

    def parser(self, data):
        data = str(data)
        data = data[:-1]
        data = data[2:]
        data = data.split('\\n')
        new_version = data[0]
        update_url = data[1]
        update_log = "\n".join(data[2:])
        return float(new_version), update_url, update_log
