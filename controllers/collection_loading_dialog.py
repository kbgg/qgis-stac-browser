import time
import urllib

from PyQt5 import uic, QtWidgets

from ..utils.config import Config
from ..utils.logging import error
from ..utils import ui
from ..threads.load_collections_thread import LoadCollectionsThread


FORM_CLASS, _ = uic.loadUiType(ui.path('collection_loading_dialog.ui'))


class CollectionLoadingDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, data={}, hooks={}, parent=None, iface=None):
        super(CollectionLoadingDialog, self).__init__(parent)

        self.data = data
        self.hooks = hooks
        self.iface = iface

        self.setupUi(self)
        self.setFixedSize(self.size())

        self.loading_thread = LoadCollectionsThread(
            Config().apis,
            on_progress=self.on_progress_update,
            on_error=self.on_error,
            on_finished=self.on_loading_finished)

        self.loading_thread.start()

    def on_progress_update(self, progress, api):
        self.label.setText(f'Loading {api}')
        self.progressBar.setValue(int(progress * 100))

    def on_error(self, e, api):
        if type(e) == urllib.error.URLError:
            error(self.iface, f'Failed to load {api.href}; {e.reason}')
        else:
            error(self.iface, f'Failed to load {api.href}; {type(e).__name__}')

    def on_loading_finished(self, apis):
        config = Config()
        config.apis = apis
        config.last_update = time.time()
        config.save()

        self.progressBar.setValue(100)
        self.hooks['on_finished'](apis)

    def closeEvent(self, event):
        if event.spontaneous():
            self.loading_thread.terminate()
            self.hooks['on_close']()
