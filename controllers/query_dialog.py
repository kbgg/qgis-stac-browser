from datetime import datetime

from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QTreeWidgetItem

from qgis.core import QgsProject, QgsMapLayer

from ..utils import ui
from ..utils.logging import debug, info, warning, error


FORM_CLASS, _ = uic.loadUiType(ui.path('query_dialog.ui'))

class QueryDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, data={}, hooks={}, parent=None, iface=None):
        super(QueryDialog, self).__init__(parent)

        self.data = data 
        self.hooks = hooks
        self.iface = iface

        self.setupUi(self)

        self._extent_layers = None
        self._catalog_tree_model = None

        self.populate_time_periods()
        self.populate_extent_layers()
        self.populate_collection_list()

        self.searchButton.clicked.connect(self.on_search_clicked)
        self.cancelButton.clicked.connect(self.on_cancel_clicked)

    def populate_time_periods(self):
        now = QtCore.QDateTime.currentDateTimeUtc()
        self.endPeriod.setDateTime(now)

    def populate_extent_layers(self):
        self._extent_layers = []
        
        layers = QgsProject.instance().mapLayers()
        for layer_key, layer in layers.items():
            if layer.type() in [QgsMapLayer.VectorLayer]:
                self._extent_layers.append(layer)

        for layer in self._extent_layers:
            self.extentLayer.addItem(layer.name())

    def populate_collection_list(self):
        self._catalog_tree_model = QStandardItemModel(self.treeView)
        for catalog in self.catalogs:
            catalog_node = QTreeWidgetItem(self.treeView)
            catalog_node.setText(0, f'{catalog.title}')
            catalog_node.setFlags(catalog_node.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
            for collection in sorted(catalog.collections):
                title = collection.title.replace("\n", " ")
                collection_node = QTreeWidgetItem(catalog_node)
                collection_node.setText(0, title)
                collection_node.setFlags(collection_node.flags() | QtCore.Qt.ItemIsUserCheckable)
                collection_node.setCheckState(0, QtCore.Qt.Unchecked)

    def validate(self):
        valid = True
        if self.extentLayer.currentIndex() < 0:
            error(self.iface, "Extent layer is not valid")
            valid = False
        start_time, end_time = self.time_period
        if start_time > end_time:
            error(self.iface, "Start time can not be after end time")
            valid = False
        return valid

    @property
    def catalog_selections(self):
        catalog_collections = []
        root = self.treeView.invisibleRootItem()
        for i in range(root.childCount()):
            catalog_node = root.child(i)
            catalog = self.catalogs[i]
            selected_collections = []
            for j in range(catalog_node.childCount()):
                collection_node = catalog_node.child(j)
                collection = self.catalogs[i].collections[j]
                if collection_node.checkState(0) == QtCore.Qt.Checked:
                    selected_collections.append(collection)

            if len(selected_collections) > 0:
                catalog_collections.append({
                    'catalog': catalog,
                    'collections': selected_collections
                    })
        return catalog_collections

    @property
    def collections(self):
        collections = []
        for catalog in sorted(self.data.get('catalogs', [])):
            collections.extend(sorted(catalog.collections))

        return collections

    @property
    def catalogs(self):
        return sorted(self.data.get('catalogs', []))

    @property
    def extent_layer(self):
        if self.extentLayer.currentIndex() >= len(self._extent_layers):
            return None

        return self._extent_layers[self.extentLayer.currentIndex()]

    @property
    def time_period(self):
        return (datetime.strptime(self.startPeriod.text(), '%Y-%m-%d %H:%MZ'),
                datetime.strptime(self.endPeriod.text(), '%Y-%m-%d %H:%MZ'))

    def on_search_clicked(self):
        valid = self.validate()
        if not valid:
            return

        self.hooks['on_search'](self.catalog_selections,
                                self.extent_layer,
                                self.time_period)

    def on_cancel_clicked(self):
        self.hooks['on_close']()

    def closeEvent(self, event):
        if event.spontaneous():
            self.hooks['on_close']()
