import os
import threading
import time
import queue

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import uic
from PyQt5 import QtWidgets

from qgis.core import QgsLogger
from ..utils.config import Config
from ..models.catalog import Catalog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'item_loading_dialog.ui'))


class ItemLoadingDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, data={}, hooks={}, parent=None):
        super(ItemLoadingDialog, self).__init__(parent)
        self.data = data
        self.hooks = hooks
        self.setupUi(self)

        self.setFixedSize(self.size())

        self.loading_thread = LoadItemsThread(self.data['catalog_collections'],
                                              self.data['extent'],
                                              self.data['start_time'],
                                              self.data['end_time'],
                                              on_progress=self.on_progress,
                                              on_finished=self.on_finished)

        self.loading_thread.start()

    def on_progress(self, collections, current_page):
        collection_label = ', '.join([c.title for c in collections])
        self.loadingLabel.setText(f'Searching {collection_label}\nPage {current_page}...')

    def on_finished(self, items):
        self.hooks['on_finished'](items)

    def closeEvent(self, event):
        if event.spontaneous():
            self.loading_thread.terminate()
            self.hooks['on_close']()

class LoadItemsThread(QThread):
    progress_signal = pyqtSignal(list, int)
    finished_signal = pyqtSignal(list)

    def __init__(self, catalog_collections, extent, start_time, end_time,
                 on_progress=None, on_finished=None):
        QThread.__init__(self)
        self._running = True
        self.current_page = 0

        self.catalog_collections = catalog_collections
        self.extent = extent
        self.start_time = start_time
        self.end_time = end_time
        self.on_progress=on_progress
        self.on_finished=on_finished
        self._current_collections = []

        self.progress_signal.connect(self.on_progress)
        self.finished_signal.connect(self.on_finished)

    def __del__(self):
        self.wait()

    def stop(self):
        self._running = False

    def run(self):
        all_items = []
        for catalog_collection in self.catalog_collections:
            if not self._running:
                return

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

    def on_next_page(self):
        self.current_page += 1
        self.progress_signal.emit(self._current_collections, self.current_page)
