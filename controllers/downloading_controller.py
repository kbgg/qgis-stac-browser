import os

from qgis.core import QgsRasterLayer, QgsProject, Qgis

from qgis.PyQt.QtWidgets import QProgressBar
from qgis.PyQt.QtCore import *

from ..utils import ui
from ..utils.logging import debug, info, warning, error
from ..threads.download_items_thread import DownloadItemsThread


class DownloadController:
    def __init__(self, data={}, hooks={}, iface=None):
        self.data = data
        self.hooks = hooks
        self.iface = iface

        self._progress_message_bar = None


        self.loading_thread = DownloadItemsThread(self.downloads,
                                                  self.download_directory,
                                                  on_progress=self.on_progress_update,
                                                  on_error=self.on_error,
                                                  on_add_layer=self.on_add_layer,
                                                  on_finished=self.on_downloading_finished)
        
        self.loading_thread.start()

    @property
    def downloads(self):
        return self.data.get('downloads', [])

    @property
    def download_directory(self):
        return self.data.get('download_directory', None)

    def on_error(self, item, e):
        error(self.iface, f'Failed to load {item.id}; {e.reason}')

    def on_add_layer(self, current_step, total_steps, item, download_directory):
        self.on_progress_update(current_step, total_steps, 'ADDING_TO_LAYERS')
        layer = QgsRasterLayer(os.path.join(download_directory, f'{item.id}.vrt'), item.id)
        QgsProject.instance().addMapLayer(layer)

    def on_destroyed(self, event):
        if not self.loading_thread.isFinished:
            self.loading_thread.terminate()

    def on_progress_update(self, current_step, total_steps, state, data={}):
        if self._progress_message_bar is None:
            self._progress_message_bar = self.iface.messageBar().createMessage('Downloading Items...')
            self._progress_message_bar.destroyed.connect(self.on_destroyed)
            self._progress = QProgressBar()
            self._progress.setMaximum(total_steps)
            self._progress.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self._progress_message_bar.layout().addWidget(self._progress)
            self.iface.messageBar().pushWidget(self._progress_message_bar, Qgis.Info)
                
        self._progress.setValue(current_step-1)

    def on_downloading_finished(self):
        self.iface.messageBar().clearWidgets()
