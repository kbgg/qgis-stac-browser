import os

from PyQt5 import uic, QtWidgets

from qgis.core import (
    QgsRasterLayer,
    QgsProject
)

from ..utils import ui
from ..utils.logging import debug, info, warning, error
from ..threads.download_items_thread import DownloadItemsThread


FORM_CLASS, _ = uic.loadUiType(ui.path('downloading_dialog.ui'))

class DownloadingDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, data={}, hooks={}, parent=None, iface=None):
        super(DownloadingDialog, self).__init__(parent)

        self.data = data
        self.hooks = hooks
        self.iface = iface

        self.setupUi(self)
        self.setFixedSize(self.size())

        self.loading_thread = DownloadItemsThread(self.items,
                                                  self.bands,
                                                  self.download_directory,
                                                  self.stream,
                                                  on_progress=self.on_progress_update,
                                                  on_error=self.on_error,
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
    
    def on_error(self, item, e):
        error(self.iface, f'Failed to load {item.id}; {e.reason}')

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


