import os
import threading
import time
import queue
import requests

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import uic
from PyQt5 import QtWidgets

from qgis.core import QgsLogger
from ..utils.config import Config
from ..models.catalog import Catalog

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'collection_loading_dialog.ui'))


class CollectionLoadingDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, data={}, hooks={}, parent=None):
        super(CollectionLoadingDialog, self).__init__(parent)
        self.data = data
        self.hooks = hooks

        self.setupUi(self)

        self.setFixedSize(self.size())


        self.loading_thread = LoadCollectionsThread(Config().get_api_list(),
                                                 on_progress=self.on_progress_update,
                                                 on_finished=self.on_loading_finished)
        
        self.loading_thread.start()

    def on_progress_update(self, progress):
        self.progressBar.setValue(int(progress*100))

    def on_loading_finished(self, collections):
        self.progressBar.setValue(100)
        
        self.hooks['on_finished'](collections)

    def closeEvent(self, event):
        if event.spontaneous():
            self.loading_thread.stop()
            self.hooks['on_close']()

class LoadCollectionsThread(QThread):
    progress_signal = pyqtSignal(float)
    finished_signal = pyqtSignal(list)

    def __init__(self, api_list, on_progress=None, on_finished=None):
        QThread.__init__(self)
        self._running = True
        self.api_list = api_list
        self.on_progress=on_progress
        self.on_finished=on_finished

        self.progress_signal.connect(self.on_progress)
        self.finished_signal.connect(self.on_finished)

    def __del__(self):
        self.wait()

    def run(self):
        all_collections = []
        for i, api_url in enumerate(self.api_list):
            if not self._running:
                return
            progress = (float(i) / float(len(self.api_list))/2)
            self.progress_signal.emit(progress)
            catalog = Catalog(url=api_url)
            collections = catalog.get_collections()
            all_collections.extend(collections)

        for i, collection in enumerate(all_collections):
            if not self._running:
                return
            progress = (float(i) / float(len(all_collections))/2) + 0.5
            self.progress_signal.emit(progress)
            collection.load()
        
        self.finished_signal.emit(all_collections)

    def stop(self):
        self._running = False
