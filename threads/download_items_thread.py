import socket
from PyQt5.QtCore import QThread, pyqtSignal
from urllib.error import URLError
from ..models.item import Item
from ..utils import fs

class DownloadItemsThread(QThread):
    progress_signal = pyqtSignal(int, int, str)
    gdal_error_signal = pyqtSignal(Exception)
    error_signal = pyqtSignal(Item, Exception)
    add_layer_signal = pyqtSignal(int, int, Item, str)
    finished_signal = pyqtSignal()

    def __init__(self, downloads, download_directory, on_progress=None, on_error=None, on_gdal_error=None, on_add_layer=None, on_finished=None):
        QThread.__init__(self)

        self.downloads = downloads
        self.download_directory = download_directory
        self.on_progress=on_progress
        self.on_error = on_error
        self.on_gdal_error = on_gdal_error
        self.on_add_layer = on_add_layer
        self.on_finished=on_finished

        self._current_item = 0

        self._current_step = 0
        self._total_steps = 0
        for download in self.downloads:
            item = download['item']
            options = download['options']
            self._total_steps += item.download_steps(options)

        self.progress_signal.connect(self.on_progress)
        self.error_signal.connect(self.on_error)
        self.gdal_error_signal.connect(self.on_gdal_error)
        self.add_layer_signal.connect(self.on_add_layer)
        self.finished_signal.connect(self.on_finished)

    def run(self):
        gdal_path = fs.gdal_path()
        for i, download in enumerate(self.downloads):
            self._current_item = i
            item = download['item']
            options = download['options']
            try:
                item.download(gdal_path, options, self.download_directory, on_update=self.on_update)
                if options.get('add_to_layers', False):
                    self.add_layer_signal.emit(self._current_step, self._total_steps, item, self.download_directory)
            except URLError as e:
                self.error_signal.emit(item, e)
            except socket.timeout as e:
                self.error_signal.emit(item, e)
            except FileNotFoundError as e:
                self.gdal_error_signal.emit(e)
        self.finished_signal.emit()

    def on_update(self, status):
        self._current_step += 1
        self.progress_signal.emit(self._current_step, self._total_steps, f'[{self._current_item + 1}/{len(self.downloads)}] {status}')
