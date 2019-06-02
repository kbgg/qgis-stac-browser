# -*- coding: utf-8 -*-

import os
import threading
import time
import queue

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import uic
from PyQt5 import QtWidgets

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'catalog_loading_dialog.ui'))


class CatalogLoadingDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None, on_finished=None):
        """Constructor."""
        super(CatalogLoadingDialog, self).__init__(parent)

        self.on_finished = on_finished
        self.setupUi(self)

        self.setFixedSize(self.size())

        self.catalogs = ['a', 'b', 'c', 'd', 'e', 'f']

        self.loading_thread = LoadCatalogsThread(self.catalogs,
                                                 on_progress=self.on_progress_update,
                                                 on_finished=self.on_loading_finished)

        self.loading_thread.start()

    def on_progress_update(self, progress):
        self.progressBar.setValue(int(progress*100))

    def on_loading_finished(self):
        self.progressBar.setValue(100)
        
        if self.on_finished is None:
            return

        self.on_finished(None)

class LoadCatalogsThread(QThread):
    progress_signal = pyqtSignal(float)
    finished_signal = pyqtSignal()

    def __init__(self, catalogs, on_progress=None, on_finished=None):
        QThread.__init__(self)
        self.catalogs = catalogs
        self.on_progress=on_progress
        self.on_finished=on_finished

        self.progress_signal.connect(self.on_progress)
        self.finished_signal.connect(self.on_finished)

    def __del__(self):
        self.wait()

    def run(self):
        for i, k in enumerate(self.catalogs):
            percent_finished = float(i) / float(len(self.catalogs))
            self.progress_signal.emit(percent_finished)
            time.sleep(0.25)

        self.finished_signal.emit()
