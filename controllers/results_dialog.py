import os

from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

from ..utils import ui
from ..utils.config import Config
from ..threads.load_preview_thread import LoadPreviewThread


FORM_CLASS, _ = uic.loadUiType(ui.path('results_dialog.ui'))


class ResultsDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, data={}, hooks={}, parent=None, iface=None):
        super(ResultsDialog, self).__init__(parent)

        self.data = data
        self.hooks = hooks
        self.iface = iface

        self.setupUi(self)

        self._item_list_model = None
        self._selected_item = None
        self._config = Config()

        self.populate_item_list()
        self.populate_download_directory()

        self.list.activated.connect(self.on_list_clicked)
        self.selectButton.clicked.connect(self.on_select_all_clicked)
        self.deselectButton.clicked.connect(self.on_deselect_all_clicked)
        self.downloadButton.clicked.connect(self.on_download_clicked)
        self.downloadPathButton.clicked.connect(self.on_download_path_clicked)
        self.backButton.clicked.connect(self.on_back_clicked)
        self.previewExternalButton.clicked.connect(self.on_preview_external_clicked)

    def populate_item_list(self):
        self._item_list_model = QtGui.QStandardItemModel(self.list)

        for item in self.items:
            i = QtGui.QStandardItem(item.id)
            i.setCheckable(True)
            self._item_list_model.appendRow(i)

        self.list.setModel(self._item_list_model)

    def populate_download_directory(self):
        self.downloadDirectory.setText(self._config.download_directory)

    def populate_item_details(self, item):
        property_keys = sorted(list(item.properties.keys()))

        self.propertiesTable.setColumnCount(2)
        self.propertiesTable.setRowCount(len(property_keys))

        for i, key in enumerate(property_keys):
            self.propertiesTable.setItem(i, 0, QtWidgets.QTableWidgetItem(key))
            self.propertiesTable.setItem(
                i,
                1,
                QtWidgets.QTableWidgetItem(str(item.properties[key]))
            )
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
        self.hooks['select_downloads'](
            self.selected_items,
            self.download_directory
        )

    def on_download_path_clicked(self):
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Download Directory",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if directory:
            self._config.download_directory = directory
            self._config.save()
            self.populate_download_directory()

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
        self.set_preview(item, False)
        self.populate_item_details(item)

    def on_image_loaded(self, item, error):
        if self._selected_item != item:
            return

        self.set_preview(item, error)

    def set_preview(self, item, error):
        self.previewExternalButton.setEnabled(False)

        if item.thumbnail_url is None:
            self.imageView.setText('No Preview Available')
            return

        if error:
            self.imageView.setText('Error Loading Preview')
            return

        if not os.path.exists(item.thumbnail_path):
            self.imageView.setText('Loading Preview...')
            self.loading_thread = LoadPreviewThread(
                item,
                on_image_loaded=self.on_image_loaded
            )
            self.loading_thread.start()
            return

        image_profile = QtGui.QImage(item.thumbnail_path)
        image_profile = image_profile.scaled(
            self.imageView.size().width(),
            self.imageView.size().height(),
            aspectRatioMode=QtCore.Qt.KeepAspectRatio,
            transformMode=QtCore.Qt.SmoothTransformation
        )
        self.imageView.setPixmap(QtGui.QPixmap.fromImage(image_profile))
        self.previewExternalButton.setEnabled(True)

    def resizeEvent(self, event):
        if self._selected_item is None:
            return

        self.set_preview(self._selected_item)

    def closeEvent(self, event):
        if event.spontaneous():
            self.hooks['on_close']()

    def on_back_clicked(self):
        self.hooks['on_back']()

    def on_preview_external_clicked(self):
        assert self._selected_item
        assert self._selected_item.thumbnail_path

        QDesktopServices.openUrl(QUrl.fromLocalFile(self._selected_item.thumbnail_path))
