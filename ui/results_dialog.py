# -*- coding: utf-8 -*-

import os

from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'results_dialog.ui'))


class ResultsDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(ResultsDialog, self).__init__(parent)
        # Set up the user interface from Designer through FORM_CLASS.
        # After self.setupUi() you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)

        self.setFixedSize(self.size())

        model = QtGui.QStandardItemModel(self.list)
        preview_path = os.path.join(os.path.dirname(__file__), 'preview.jpg')
        self.items = {
            'S2B_9VXK_20171013_0': {
                    'thumbnail': preview_path,
                    'properties': {
                            'collection': 'sentinel-2-l1c',
                            'datetime': '2017-10-13T20:03:46.461000+00:00',
                            'eo:platform': 'sentinel-2b',
                            'eo:cloud_cover': 41.52,
                            'sentinel:utm_zone': 9,
                            'sentinel:latitude_band': 'V',
                            'sentinel:grid_square': 'XK',
                            'sentinel:sequence': '0',
                            'sentinel:product_id': 'S2B_MSIL1C_20171013T200349_N0205_R128_T09VXK_20171013T200346'
                        }
                    },
            'S2B_9VXK_20171014_0': {
                    'thumbnail': None,
                    'properties': {

                        }
                    },
            'S2B_9VXK_20171015_0': {
                    'thumbnail': preview_path,
                    'properties': {

                        }
                    },
        }

        for collection in sorted(list(self.items.keys())):
            item = QtGui.QStandardItem(collection.replace('\n', ' '))
            item.setCheckable(True)
            model.appendRow(item)

        self.list.setModel(model)

        self.list.clicked.connect(self.on_list_clicked)

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def on_list_clicked(self, index):
        items = self.list.selectedIndexes()
        item_id = sorted(list(self.items.keys()))[int(items[0].row())]
        self.load_item(item_id)

    def load_item(self, item_id):
        data = self.items[item_id]
        if data['thumbnail'] is not None:
            image_profile = QtGui.QImage(data['thumbnail'])
            image_profile = image_profile.scaled(250, 250,
                                                 aspectRatioMode=QtCore.Qt.KeepAspectRatio,
                                                 transformMode=QtCore.Qt.SmoothTransformation)
            self.imageView.setPixmap(QtGui.QPixmap.fromImage(image_profile))
        else:
            self.imageView.setText('No Preview Available')

        property_keys = sorted(list(data['properties'].keys()))

        self.propertiesTable.setColumnCount(2)
        self.propertiesTable.setRowCount(len(property_keys))

        for i, key in enumerate(property_keys):
            self.propertiesTable.setItem(i, 0, QtWidgets.QTableWidgetItem(key))
            self.propertiesTable.setItem(i, 1, QtWidgets.QTableWidgetItem(str(data['properties'][key])))
        self.propertiesTable.resizeColumnsToContents()
