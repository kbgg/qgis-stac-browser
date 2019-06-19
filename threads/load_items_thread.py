from PyQt5.QtCore import QThread, pyqtSignal
from urllib.error import URLError

class LoadItemsThread(QThread):
    progress_signal = pyqtSignal(list, int)
    error_signal = pyqtSignal(Exception)
    finished_signal = pyqtSignal(list)

    def __init__(self, catalog_collections, extent, start_time, end_time,
                 on_progress=None, on_error=None, on_finished=None):
        QThread.__init__(self)
        self.current_page = 0

        self.catalog_collections = catalog_collections
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
            for catalog_collection in self.catalog_collections:
                catalog = catalog_collection['catalog']
                collections = catalog_collection['collections']
                self._current_collections = collections
                
                items = catalog.api.search_items(collections,
                                                 self.extent,
                                                 self.start_time,
                                                 self.end_time,
                                                 on_next_page=self.on_next_page)
                all_items.extend(items)
            self.finished_signal.emit(all_items)
        except URLError as e:
            self.error_signal.emit(e)

    def on_next_page(self):
        self.current_page += 1
        self.progress_signal.emit(self._current_collections, self.current_page)
