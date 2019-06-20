from PyQt5.QtCore import QThread, pyqtSignal
from urllib.error import URLError
from ..models.api import API

class LoadCollectionsThread(QThread):
    progress_signal = pyqtSignal(float, str)
    error_signal = pyqtSignal(Exception, API)
    finished_signal = pyqtSignal(list)

    def __init__(self, api_list, on_progress=None, on_error=None, on_finished=None):
        QThread.__init__(self)

        self.api_list = api_list
        self.on_progress=on_progress
        self.on_error = on_error
        self.on_finished=on_finished

        self.progress_signal.connect(self.on_progress)
        self.error_signal.connect(self.on_error)
        self.finished_signal.connect(self.on_finished)

    def run(self):
        apis = []
        for i, api in enumerate(self.api_list):
            progress = (float(i) / float(len(self.api_list)))
            self.progress_signal.emit(progress, api.href)
            try:
                api.load()
                apis.append(api)
            except URLError as e:
                self.error_signal.emit(e, api)
        
        self.finished_signal.emit(apis)
