from PyQt5.QtCore import QThread, pyqtSignal
from urllib.error import URLError
from ..models.api import API

class LoadItemsThread(QThread):
    progress_signal = pyqtSignal(API, list, int)
    error_signal = pyqtSignal(Exception)
    finished_signal = pyqtSignal(list)

    def __init__(self, api_collections, extent, start_time, end_time,
                 on_progress=None, on_error=None, on_finished=None):
        QThread.__init__(self)
        self.current_page = 0

        self.api_collections = api_collections
        self.extent = extent
        self.start_time = start_time
        self.end_time = end_time
        self.on_progress = on_progress
        self.on_error = on_error
        self.on_finished = on_finished
        self._current_collections = []
        
        self.progress_signal.connect(self.on_progress)
        self.error_signal.connect(self.on_error)
        self.finished_signal.connect(self.on_finished)

    def run(self):
        try:
            all_items = []
            for api_collection in self.api_collections:
                self.current_page = 0
                api = api_collection['api']
                collections = api_collection['collections']
                self._current_collections = collections
                
                items = api.search_items(collections,
                                         self.extent,
                                         self.start_time,
                                         self.end_time,
                                         on_next_page=self.on_next_page)
                all_items.extend(items)
            self.finished_signal.emit(all_items)
        except URLError as e:
            self.error_signal.emit(e)

    def on_next_page(self, api):
        self.current_page += 1
        self.progress_signal.emit(api, self._current_collections, self.current_page)
