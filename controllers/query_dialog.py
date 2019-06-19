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
        self._api_tree_model = None

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
        self._api_tree_model = QStandardItemModel(self.treeView)
        for api in self.apis:
            api_node = QTreeWidgetItem(self.treeView)
            api_node.setText(0, f'{api.title}')
            api_node.setFlags(api_node.flags() | QtCore.Qt.ItemIsTristate | QtCore.Qt.ItemIsUserCheckable)
            api_node.setCheckState(0, QtCore.Qt.Unchecked)
            for collection in sorted(api.collections):
                title = collection.title.replace("\n", " ")
                collection_node = QTreeWidgetItem(api_node)
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
    def api_selections(self):
        api_collections = []
        root = self.treeView.invisibleRootItem()
        for i in range(root.childCount()):
            api_node = root.child(i)
            api = self.apis[i]
            selected_collections = []
            for j in range(api_node.childCount()):
                collection_node = api_node.child(j)
                collection = api.collections[j]
                if collection_node.checkState(0) == QtCore.Qt.Checked:
                    selected_collections.append(collection)

            if api_node.checkState(0) == QtCore.Qt.Checked or api_node.checkState(0) == QtCore.Qt.PartiallyChecked:
                api_collections.append({
                    'api': api,
                    'collections': selected_collections
                    })
        return api_collections

    @property
    def apis(self):
        return sorted(self.data.get('apis', []))

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

        self.hooks['on_search'](self.api_selections,
                                self.extent_layer,
                                self.time_period)

    def on_cancel_clicked(self):
        self.hooks['on_close']()

    def closeEvent(self, event):
        if event.spontaneous():
            self.hooks['on_close']()
