import os
import time

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

import requests
import shutil

from ..models.item import Item

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'results_dialog.ui'))


class ResultsDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, data={}, hooks={}, parent=None):
        super(ResultsDialog, self).__init__(parent)
        self.data = data
        self.hooks = hooks
        self.setupUi(self)
        
        self.selected_item = None
        
        # Populate Item List
        model = QtGui.QStandardItemModel(self.list)
        
        for item in self.get_items():
            i = QtGui.QStandardItem(item.get_id())
            i.setCheckable(True)
            model.appendRow(i)

        self.list_model = model
        self.list.setModel(model)

        # Connect Buttons
        self.list.activated.connect(self.on_list_clicked)
        self.selectButton.clicked.connect(self.on_select_all_clicked)
        self.deselectButton.clicked.connect(self.on_deselect_all_clicked)
        self.downloadButton.clicked.connect(self.on_download_clicked)
        self.backButton.clicked.connect(self.on_back_clicked)

    def get_items(self):
        return sorted(self.data['items'])

    def on_download_clicked(self):
        for i in range(self.list_model.rowCount()):
            item = self.list_model.item(i)
            if item.checkState() != QtCore.Qt.Checked:
                continue
            
            self.get_items()[i].download()

    def on_select_all_clicked(self):
        for i in range(self.list_model.rowCount()):
            item = self.list_model.item(i)
            item.setCheckState(QtCore.Qt.Checked)
    
    def on_deselect_all_clicked(self):
        for i in range(self.list_model.rowCount()):
            item = self.list_model.item(i)
            item.setCheckState(QtCore.Qt.Unchecked)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_list_clicked(self, index):
        items = self.list.selectedIndexes()
        item = self.get_items()[items[0].row()]
        self.load_item(item)

    def load_item(self, item):
        self.selected_item = item
        self.set_preview(item)

        property_keys = sorted(list(item.get_properties().keys()))

        self.propertiesTable.setColumnCount(2)
        self.propertiesTable.setRowCount(len(property_keys))

        for i, key in enumerate(property_keys):
            self.propertiesTable.setItem(i, 0, QtWidgets.QTableWidgetItem(key))
            self.propertiesTable.setItem(i, 1, QtWidgets.QTableWidgetItem(str(item.get_properties()[key])))
        self.propertiesTable.resizeColumnsToContents()

    def on_image_loaded(self, item):
        if self.selected_item != item:
            return

        self.set_preview(item)

    def set_preview(self, item):
        if item.get_thumbnail_url() is None:
            self.imageView.setText('No Preview Available')
            return

        if not os.path.exists(item.get_thumbnail_path()):
            self.imageView.setText('Loading Preview...')
            self.loading_thread = LoadPreviewThread(item, on_image_loaded=self.on_image_loaded)
            self.loading_thread.start()
            return

        image_profile = QtGui.QImage(item.get_thumbnail_path())
        image_profile = image_profile.scaled(self.imageView.size().width(),
                                             self.imageView.size().height(),
                                             aspectRatioMode=QtCore.Qt.KeepAspectRatio,
                                             transformMode=QtCore.Qt.SmoothTransformation)
        self.imageView.setPixmap(QtGui.QPixmap.fromImage(image_profile))

    def resizeEvent(self, event):
        if self.selected_item is None:
            return

        self.set_preview(self.selected_item)
    
    def closeEvent(self, event):
        if event.spontaneous():
            self.hooks['on_close']()

    def on_back_clicked(self):
        self.hooks['on_back']()


class LoadPreviewThread(QThread):
    finished_signal = pyqtSignal(Item)

    def __init__(self, item, on_image_loaded=None):
        QThread.__init__(self)
        self.item = item
        self.on_image_loaded=on_image_loaded

        self.finished_signal.connect(self.on_image_loaded)

    def __del__(self):
        self.wait()

    def run(self):
        r = requests.get(self.item.get_thumbnail_url(), stream=True)
        if r.status_code == 200:
            with open(self.item.get_thumbnail_path(), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        self.finished_signal.emit(self.item)
