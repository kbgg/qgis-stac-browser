from PyQt5.QtCore import QThread, pyqtSignal
from urllib.error import URLError
from ..models.item import Item

class DownloadItemsThread(QThread):
    progress_signal = pyqtSignal(int, int, str, dict)
    error_signal = pyqtSignal(Item, Exception)
    add_layer_signal = pyqtSignal(int, int, Item, str)
    finished_signal = pyqtSignal()

    def __init__(self, items, bands, download_directory, stream, on_progress=None, on_error=None, on_add_layer=None, on_finished=None):
        QThread.__init__(self)

        self.items = items
        self.bands = bands
        self.download_directory = download_directory
        self.stream = stream
        self.on_progress=on_progress
        self.on_error = on_error
        self.on_add_layer = on_add_layer
        self.on_finished=on_finished

        self._current_item = None

        self.progress_signal.connect(self.on_progress)
        self.error_signal.connect(self.on_error)
        self.add_layer_signal.connect(self.on_add_layer)
        self.finished_signal.connect(self.on_finished)

    def run(self):
        for i, item in enumerate(self.items):
            self._current_item = i
            bands = []
            for collection_band in self.bands:
                if collection_band['collection'] == item.collection:
                    bands = collection_band['bands']
            try:
                item.download(bands, self.download_directory, self.stream, on_update=self.on_update)
                self.add_layer_signal.emit(i, len(self.items), item, self.download_directory)
            except URLError as e:
                self.error_signal.emit(item, e)
        self.finished_signal.emit()

    def on_update(self, state, data={}):
        self.progress_signal.emit(self._current_item, len(self.items), state, data)
