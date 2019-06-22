import socket
from PyQt5.QtCore import QThread, pyqtSignal
from urllib.error import URLError
from ..utils import network
from ..models.item import Item

class LoadPreviewThread(QThread):
    finished_signal = pyqtSignal(Item, bool)

    def __init__(self, item, on_image_loaded=None):
        QThread.__init__(self)
        self.item = item
        self.on_image_loaded=on_image_loaded

        self.finished_signal.connect(self.on_image_loaded)

    def run(self):
        try:
            network.download(self.item.thumbnail_url, self.item.thumbnail_path)
            self.finished_signal.emit(self.item, False)
        except URLError as e:
            self.finished_signal.emit(self.item, True)
        except socket.timeout as e:
            self.finished_signal.emit(self.item, True)
