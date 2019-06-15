import os
import time

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtWidgets import QFileDialog

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

        self._item_list_model = None
        self._selected_item = None

        self.populate_item_list()
        
        self.list.activated.connect(self.on_list_clicked)
        self.selectButton.clicked.connect(self.on_select_all_clicked)
        self.deselectButton.clicked.connect(self.on_deselect_all_clicked)
        self.downloadButton.clicked.connect(self.on_download_clicked)
        self.downloadPathButton.clicked.connect(self.on_download_path_clicked)
        self.backButton.clicked.connect(self.on_back_clicked)

    def populate_item_list(self):
        self._item_list_model = QtGui.QStandardItemModel(self.list)
        
        for item in self.items:
            i = QtGui.QStandardItem(item.id)
            i.setCheckable(True)
            self._item_list_model.appendRow(i)

        self.list.setModel(self._item_list_model)

    def populate_item_details(self, item):
        property_keys = sorted(list(item.properties.keys()))

        self.propertiesTable.setColumnCount(2)
        self.propertiesTable.setRowCount(len(property_keys))

        for i, key in enumerate(property_keys):
            self.propertiesTable.setItem(i, 0, QtWidgets.QTableWidgetItem(key))
            self.propertiesTable.setItem(i, 1, QtWidgets.QTableWidgetItem(str(item.properties[key])))
        self.propertiesTable.resizeColumnsToContents()
    
    @property
    def items(self):
        return sorted(self.data.get('items', []))

    @property
    def selected_items(self):
        selected_items = []
        for i in range(self._item_list_model.rowCount()):
            if self._item_list_model.item(i).checkState() == QtCore.Qt.Checked:
                selected_items.append(self.items[i])

        return selected_items

    @property
    def download_directory(self):
        return self.downloadDirectory.text()

    def on_download_clicked(self):
        self.hooks['select_bands'](self.selected_items, self.download_directory)

    def on_download_path_clicked(self):
        directory = QFileDialog.getExistingDirectory(self, 
                                                     "Select Download Directory", 
                                                     "", 
                                                     QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if directory:
            self.downloadDirectory.setText(directory)

    def on_select_all_clicked(self):
        for i in range(self._item_list_model.rowCount()):
            item = self._item_list_model.item(i)
            item.setCheckState(QtCore.Qt.Checked)
    
    def on_deselect_all_clicked(self):
        for i in range(self._item_list_model.rowCount()):
            item = self._item_list_model.item(i)
            item.setCheckState(QtCore.Qt.Unchecked)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_list_clicked(self, index):
        items = self.list.selectedIndexes()
        for i in items:
            item = self.items[i.row()]
            self.select_item(item)

    def select_item(self, item):
        self._selected_item = item
        self.set_preview(item)
        self.populate_item_details(item)

    def on_image_loaded(self, item):
        if self._selected_item != item:
            return

        self.set_preview(item)

    def set_preview(self, item):
        if item.thumbnail_url is None:
            self.imageView.setText('No Preview Available')
            return

        if not os.path.exists(item.thumbnail_path):
            self.imageView.setText('Loading Preview...')
            self.loading_thread = LoadPreviewThread(item, on_image_loaded=self.on_image_loaded)
            self.loading_thread.start()
            return

        image_profile = QtGui.QImage(item.thumbnail_path)
        image_profile = image_profile.scaled(self.imageView.size().width(),
                                             self.imageView.size().height(),
                                             aspectRatioMode=QtCore.Qt.KeepAspectRatio,
                                             transformMode=QtCore.Qt.SmoothTransformation)
        self.imageView.setPixmap(QtGui.QPixmap.fromImage(image_profile))

    def resizeEvent(self, event):
        if self._selected_item is None:
            return

        self.set_preview(self._selected_item)
    
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
        r = requests.get(self.item.thumbnail_url, stream=True)
        if r.status_code == 200:
            with open(self.item.thumbnail_path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
        self.finished_signal.emit(self.item)
