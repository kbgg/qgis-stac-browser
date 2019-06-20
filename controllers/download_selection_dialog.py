from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from qgis.core import QgsProject, QgsMapLayer

from ..utils import ui
from pprint import pprint


FORM_CLASS, _ = uic.loadUiType(ui.path('download_selection_dialog.ui'))

class DownloadSelectionDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, data={}, hooks={}, parent=None, iface=None):
        super(DownloadSelectionDialog, self).__init__(parent)

        self.data = data 
        self.hooks = hooks
        self.iface = iface

        self.setupUi(self)
        
        self._current_item_index = 0
        self._downloads = []

        self.populate_current_item()

        self.nextButton.clicked.connect(self.on_next_clicked)
        self.cancelButton.clicked.connect(self.on_cancel_clicked)

    def populate_current_item(self):
        if self._current_item_index + 1 == len(self.items):
            self.nextButton.setText('Download')
        else:
            self.nextButton.setText('Next')
    

        collection_label = 'N/A'
        if self.current_item.collection is not None:
            collection_label = self.current_item.collection.id
        self.itemLabel.setText(self.current_item.id)
        self.collectionLabel.setText(collection_label)
        
        self.assetListWidget.clear()
        for asset in sorted(self.current_item.assets):
            asset_node = QtWidgets.QListWidgetItem(self.assetListWidget)
            asset_node.setText(f'{asset.title}')
            asset_node.setFlags(asset_node.flags() | QtCore.Qt.ItemIsUserCheckable)
            asset_node.setCheckState(QtCore.Qt.Unchecked)

    def add_current_item_to_downloads(self):
        apply_to_all = (self.applyAllCheckbox.checkState() == QtCore.Qt.Checked)
        add_to_layers = (self.addLayersCheckbox.checkState() == QtCore.Qt.Checked)
        stream_cogs = (self.streamCheckbox.checkState() == QtCore.Qt.Checked)

        download_data = {
                            'item': self.current_item,
                            'options': {
                                'add_to_layers': add_to_layers,
                                'stream_cogs': stream_cogs,
                                'assets': [a.key for a in self.selected_assets],
                            },
                }

        self.downloads.append(download_data)

        if not apply_to_all or self.current_item.collection is None:
            return

        for i in range(self._current_item_index, len(self.items)):
            if self.item_in_downloads(self.items[i]):
                continue

            if self.items[i].collection is None:
                continue

            if self.items[i].collection == self.current_item.collection:
                download_data = {
                                    'item': self.items[i],
                                    'options': {
                                        'add_to_layers': add_to_layers,
                                        'stream_cogs': stream_cogs,
                                        'assets': [a.key for a in self.selected_assets],
                                    },
                                }
                self.downloads.append(download_data)

    def item_in_downloads(self, item):
        for d in self.downloads:
            if d['item'] == item:
                return True

        return False

    @property
    def downloads(self):
        return self._downloads

    @property
    def selected_assets(self):
        sorted_assets = sorted(self.current_item.assets)
        assets = []
        for i in range(self.assetListWidget.count()):
            asset_node = self.assetListWidget.item(i)
            if asset_node.checkState() != QtCore.Qt.Checked:
                continue
            assets.append(sorted_assets[i])

        return assets

    @property
    def current_item(self):
        if self._current_item_index >= len(self.items):
            return None

        return self.items[self._current_item_index]

    @property
    def items(self):
        return sorted(self.data.get('items', []))

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

    @property
    def next_item(self):
        if self._current_item_index + 1 >= len(self.items):
            return None

        return self.items[self._current_item_index + 1]

    def on_next_clicked(self):
        self.add_current_item_to_downloads()
        
        self._current_item_index += 1
        while self.current_item is not None:
            if not self.item_in_downloads(self.current_item):
                break
            self._current_item_index += 1

        if self.current_item is None:
            self.accept()
            return

        self.populate_current_item()

    def on_cancel_clicked(self):
        self.reject()

    def closeEvent(self, event):
        if event.spontaneous():
            self.reject()
