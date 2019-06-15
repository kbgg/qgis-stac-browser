import os
from datetime import datetime

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from qgis.core import QgsProject, QgsMapLayer

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'select_bands_dialog.ui'))


class SelectBandsDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, data={}, hooks={}, parent=None):
        super(SelectBandsDialog, self).__init__(parent)
        self.data = data 
        self.hooks = hooks
        self.setupUi(self)

        self._bands_tree_model = None

        self.populate_bands_list()

        self.downloadButton.clicked.connect(self.on_download_clicked)
        self.cancelButton.clicked.connect(self.on_cancel_clicked)
    
    def populate_bands_list(self):
        self._bands_tree_model = QStandardItemModel(self.treeView)
        for collection in self.collections:
            print(collection)
            collection_node = QStandardItem(f'{collection.title}')
            for band_name, band_data in collection.bands.items():
                if band_data.get('common_name', None) is not None:
                    band_node = QStandardItem(f'{band_name} ({band_data.get("common_name")})')
                else:
                    band_node = QStandardItem(band_name)
                band_node.setCheckable(True)
                collection_node.appendRow(band_node)
            self._bands_tree_model.appendRow(collection_node)

        self.treeView.setModel(self._bands_tree_model)
        self.treeView.expandAll()

    def on_download_clicked(self):
        self.accept()

    def on_cancel_clicked(self):
        self.reject()

    @property
    def items(self):
        return self.data.get('items', [])

    @property
    def stream(self):
        return self.cogCheckbox.checkState() == QtCore.Qt.Checked

    @property
    def collections(self):
        collections = []
        for item in self.items:
            if item.collection not in collections:
                collections.append(item.collection)

        return sorted(collections)

    @property
    def selected_bands(self):
        collection_band_list = []
        for i in range(len(self.collections)):
            collection = self.collections[i]
            collection_node = self._bands_tree_model.item(i)
            bands = list(collection.bands.items())
            selected_bands = []
            for j in range(collection_node.rowCount()):
                band_node = collection_node.child(j)
                band_name, band_data = bands[j]

                if band_node.checkState() == QtCore.Qt.Checked:
                    selected_bands.append(band_name)

            if len(selected_bands) > 0:
                collection_band_list.append({
                    'collection': collection,
                    'bands': selected_bands
                    })

        return collection_band_list


    def closeEvent(self, event):
        if event.spontaneous():
            self.reject()
