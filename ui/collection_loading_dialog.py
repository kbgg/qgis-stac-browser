import os
import threading
import time
import queue

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import uic
from PyQt5 import QtWidgets

from qgis.core import QgsLogger
from ..utils.config import Config
from ..models.api import API
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

    def on_progress_update(self, progress, api):
        self.label.setText(f'Loading {api}')
        self.progressBar.setValue(int(progress*100))

    def on_loading_finished(self, apis):
        self.progressBar.setValue(100)
        self.hooks['on_finished'](apis)

    def closeEvent(self, event):
        if event.spontaneous():
            self.loading_thread.terminate()
            self.hooks['on_close']()

class LoadCollectionsThread(QThread):
    progress_signal = pyqtSignal(float, str)
    finished_signal = pyqtSignal(list)

    def __init__(self, api_list, on_progress=None, on_finished=None):
        QThread.__init__(self)
        self._running = True
        self.api_list = api_list
        self.on_progress=on_progress
        self.on_finished=on_finished

        self.progress_signal.connect(self.on_progress)
        self.finished_signal.connect(self.on_finished)

    def run(self):
        apis = []
        for i, api_url in enumerate(self.api_list):
            if not self._running:
                return
            progress = (float(i) / float(len(self.api_list)))
            self.progress_signal.emit(progress, api_url)
            api = API(api_url)
            api.catalog.load_collections()
            apis.append(api)
        
        self.finished_signal.emit(apis)
        self.quit()

    def stop(self):
        self._running = False
