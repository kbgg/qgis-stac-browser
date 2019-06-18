import os
import threading
import time
import queue

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import uic
from PyQt5 import QtWidgets

from qgis.core import (
    QgsRasterLayer,
    QgsProject
)

from qgis.core import QgsLogger
from ..utils.config import Config
from ..models.catalog import Catalog
from ..models.item import Item

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'downloading_dialog.ui'))


class DownloadingDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, data={}, hooks={}, parent=None):
        super(DownloadingDialog, self).__init__(parent)
        self.data = data
        self.hooks = hooks

        self.setupUi(self)

        self.setFixedSize(self.size())

        self.loading_thread = DownloadItemsThread(self.items,
                                                  self.bands,
                                                  self.download_directory,
                                                  self.stream,
                                                  on_progress=self.on_progress_update,
                                                  on_add_layer=self.on_add_layer,
                                                  on_finished=self.on_downloading_finished)
        
        self.loading_thread.start()

    @property
    def items(self):
        return self.data.get('items', [])

    @property
    def bands(self):
        return self.data.get('bands', [])

    @property
    def download_directory(self):
        return self.data.get('download_directory', None)

    @property
    def stream(self):
        return self.data.get('stream', False)

    def on_add_layer(self, current_item, total_items, item, download_directory):
        self.on_progress_update(current_item, total_items, 'ADDING_TO_LAYERS')
        layer = QgsRasterLayer(os.path.join(download_directory, f'{item.id}.vrt'), item.id)
        QgsProject.instance().addMapLayer(layer)

    def on_progress_update(self, current_item, total_items, state, data={}):
        self.totalLabel.setText(f'Item {current_item+1} of {total_items}')
        progress = int((current_item / total_items) * 100)
        self.totalProgress.setValue(progress)

        total_bands = len(data.get('bands', []))
        total_steps = total_bands + 2
        if state == 'DOWNLOADING_BAND':
            current_band = data.get('band', '???')
            self.itemLabel.setText(f'Downloading Band {current_band}')
            current_step = data.get('bands', []).index(current_band) + 1
        elif state == 'BUILDING_VRT':
            self.itemLabel.setText('Building Virtual Raster')
            current_step = total_bands + 1
        elif state == 'ADDING_TO_LAYERS':
            self.itemLabel.setText('Adding to Layers')
            current_step = total_bands + 2

        progress = int(((current_step - 1) / total_steps) * 100)
        self.itemProgress.setValue(progress)

    def on_downloading_finished(self):
        self.totalProgress.setValue(100)
        self.itemProgress.setValue(100)
        self.hooks['on_finished']()

    def closeEvent(self, event):
        if event.spontaneous():
            self.loading_thread.terminate()
            self.hooks['on_close']()

class DownloadItemsThread(QThread):
    progress_signal = pyqtSignal(int, int, str, dict)
    add_layer_signal = pyqtSignal(int, int, Item, str)
    finished_signal = pyqtSignal()

    def __init__(self, items, bands, download_directory, stream, on_progress=None, on_add_layer=None, on_finished=None):
        QThread.__init__(self)
        self._running = True
        self.items = items
        self.bands = bands
        self.download_directory = download_directory
        self.stream = stream
        self.on_progress=on_progress
        self.on_add_layer = on_add_layer
        self.on_finished=on_finished

        self._current_item = None

        self.progress_signal.connect(self.on_progress)
        self.add_layer_signal.connect(self.on_add_layer)
        self.finished_signal.connect(self.on_finished)

    def __del__(self):
        self.wait()

    def run(self):
        for i, item in enumerate(self.items):
            self._current_item = i
            bands = []
            for collection_band in self.bands:
                if collection_band['collection'] == item.collection:
                    bands = collection_band['bands']
            item.download(bands, self.download_directory, self.stream, on_update=self.on_update)
            self.add_layer_signal.emit(i, len(self.items), item, self.download_directory)
        self.finished_signal.emit()

    def on_update(self, state, data={}):
        self.progress_signal.emit(self._current_item, len(self.items), state, data)

