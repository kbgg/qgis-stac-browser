from PyQt5.QtCore import QThread, pyqtSignal
from urllib.error import URLError
from ..models.api import API

class LoadAPIDataThread(QThread):
    error_signal = pyqtSignal(Exception)
    finished_signal = pyqtSignal(API)

    def __init__(self, api, on_error=None, on_finished=None):
        QThread.__init__(self)
        self.api = api

        self.on_error = on_error
        self.on_finished = on_finished
        
        self.error_signal.connect(self.on_error)
        self.finished_signal.connect(self.on_finished)

    def run(self):
        try:
            self.api.load()
            self.finished_signal.emit(self.api)
        except URLError as e:
            self.error_signal.emit(e)
