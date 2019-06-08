import os
from datetime import datetime

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from qgis.core import QgsProject

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'query_dialog.ui'))


class QueryDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, data={}, hooks={}, parent=None):
        super(QueryDialog, self).__init__(parent)
        self.data = data
        self.hooks = hooks
        self.setupUi(self)

        now = QtCore.QDateTime.currentDateTimeUtc()

        self.endPeriod.setDateTime(now)

        layers = QgsProject.instance().mapLayers()
        self.eligible_layers = []
        for layer_key, layer in layers.items():
            if layer.type() in [0]:
                self.eligible_layers.append(layer)

        for layer in self.eligible_layers:
            self.extentLayer.addItem(layer.name())

        self.list_model = QStandardItemModel(self.list)
        
        for collection in self.get_collections():
            collection_title = collection.get_title().replace('\n', ' ')
            item = QStandardItem(f'{collection_title} [{collection.get_parent().get_title()}]')
            item.setCheckable(True)
            self.list_model.appendRow(item)

        self.list.setModel(self.list_model)

        self.searchButton.clicked.connect(self.on_search_clicked)
        self.cancelButton.clicked.connect(self.on_cancel_clicked)

    def on_search_clicked(self):
        selected_collections = self.get_selected_collections()
        catalog_collections = {}

        for collection in selected_collections:
            if catalog_collections.get(collection.get_parent().get_url(), None) is None:
                catalog_collections[collection.get_parent().get_url()] = []
            catalog_collections[collection.get_parent().get_url()].append(collection)

        self.hooks['on_search'](catalog_collections,
                                self.get_extent_layer(),
                                self.get_time_period())

    def on_cancel_clicked(self):
        self.hooks['on_close']()

    def get_collections(self):
        return sorted(self.data['collections'])

    def get_extent_layer(self):
        for i, layer in enumerate(self.eligible_layers):
            if i == self.extentLayer.currentIndex():
                return layer

        return None

    def get_time_period(self):
        return (datetime.strptime(self.startPeriod.text(), '%Y-%m-%d %H:%MZ'),
                datetime.strptime(self.endPeriod.text(), '%Y-%m-%d %H:%MZ'))

    def get_selected_collections(self):
        selected_collections = []
        all_collections = self.get_collections()

        for row in range(self.list_model.rowCount()):
            item = self.list_model.item(row)
            if item.checkState() == QtCore.Qt.Checked:
                selected_collections.append(all_collections[row])

        return selected_collections

    def closeEvent(self, event):
        if event.spontaneous():
            self.hooks['on_close']()
