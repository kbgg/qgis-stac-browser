import re

from PyQt5 import uic
from PyQt5.QtWidgets import (
    QWidget, QAction, QMenu, QVBoxLayout, QDialog, QDialogButtonBox)

import qgis.utils

from qgis.core import (
    QgsProject, QgsMapLayerProxyModel, QgsRectangle, QgsReferencedRectangle,
    QgsPointXY, QgsCoordinateReferenceSystem)
from qgis.gui import QgsMapLayerComboBox
from processing.gui.RectangleMapTool import RectangleMapTool

from ..utils import ui


FORM_CLASS, _ = uic.loadUiType(ui.path('extent_selector.ui'))


class ExtentSelector(QWidget, FORM_CLASS):
    """Helper widget to provide extent selection functionality.

    Mimics the UI behaviour of the qgis.processing.gui.ExtentSelectionPanel
    """

    EXTRACT_REGEX = r'(-?\d+(\.\d+)?) (-?\d+(\.\d+)?), (-?\d+(\.\d+)?) (-?\d+(\.\d+)?) \[(EPSG:(\d{2,}))\]'

    def __init__(self, parent=None, iface=None, filters=None):
        """Constructor."""
        super(ExtentSelector, self).__init__(parent)

        self.setupUi(self)

        # self.dialog is used by RectangleMapTool!!!
        self.dialog = parent
        self.iface = iface if iface else qgis.utils.iface
        self.canvas = iface.mapCanvas()
        self.prev_map_tool = self.canvas.mapTool()
        self.tool = RectangleMapTool(self.canvas)

        self.tool.rectangleCreated.connect(self.on_tool_update_extent)

        self.actionCanvas = QAction('Use canvas extent', self.menuButton)
        self.actionLayer = QAction('Use layer extent', self.menuButton)
        self.actionSelection = QAction('Draw extent...', self.menuButton)

        self.actionCanvas.setToolTip('')
        self.actionLayer.setToolTip('')
        self.actionSelection.setToolTip('')

        self.menu = QMenu()
        self.menu.addAction(self.actionCanvas)
        self.menu.addAction(self.actionLayer)
        self.menu.addSeparator()
        self.menu.addAction(self.actionSelection)

        self.menuButton.setMenu(self.menu)

        self.extent_layer_dialog = self._init_extent_layer_dialog()

        self.actionCanvas.triggered.connect(self.on_action_canvas_triggered)
        self.actionLayer.triggered.connect(self.on_action_layer_triggered)
        self.actionSelection.triggered.connect(
            self.on_action_selection_triggered)
        self.extent_layer_dialog.accepted.connect(
            self.on_extent_layer_dialog_accepted)
        self.lineEdit.textChanged.connect(self.on_line_textchanged)

    def _init_extent_layer_dialog(self, filters=QgsMapLayerProxyModel.All):
        dialog = QDialog()
        layout = QVBoxLayout()
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        layer_combobox = QgsMapLayerComboBox()

        layout.addWidget(layer_combobox)
        layout.addWidget(buttons)

        layer_combobox.setFilters(filters)
        layer_combobox.setAccessibleName('')
        dialog.setModal(True)
        dialog.setLayout(layout)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        # ugly, but better to keep the function as pure as possible pure.
        # I guess it begs for it's own class
        dialog.layer_combobox = layer_combobox

        return dialog

    def is_valid(self, value=None):
        """Check if input string is valid."""
        if value is None:
            value = self.lineEdit.text()

        if re.match(self.EXTRACT_REGEX, value):
            return True
        else:
            return False

    def value(self):
        """Mimic the QT API to get the value."""
        # Even though it is more work, everytime we should convert the
        # rectangle to string and then parse the string back to a rectangle.
        # This way there is only single source of
        # truth and will keep away a lot of tricky bugs

        value = self.lineEdit.text().strip()

        if not self.is_valid(value):
            return None

        [x1, _, y1, _, x2, _, y2, _, epsg, crs_code] = re.findall(
            self.EXTRACT_REGEX, value)[0]

        p1 = QgsPointXY(float(x1), float(y1))
        p2 = QgsPointXY(float(x2), float(y2))
        rect = QgsReferencedRectangle(
            QgsRectangle(p1, p2),
            QgsCoordinateReferenceSystem(int(crs_code)))

        return rect

    def toggle_line_validity(self, is_valid=None):
        """Set the input with red class if not valid."""
        if is_valid is None:
            is_valid = self.is_valid()

        if is_valid:
            self.lineEdit.setStyleSheet('color: inherit;')
        else:
            self.lineEdit.setStyleSheet('color: red;')

    def on_line_textchanged(self, value):
        """Triggered when the input changes, even programatically."""
        self.toggle_line_validity()

    def on_extent_layer_dialog_accepted(self):
        """Triggered when a layer is selected and dialog accepted."""
        layer = self.extent_layer_dialog.layer_combobox.currentLayer()
        self.set_value_from_layer(layer)

    def on_action_canvas_triggered(self):
        """Triggered when menu action "canvas" is clicked."""
        self.set_value_from_rect(self.canvas.extent())

    def on_action_layer_triggered(self, filters):
        """Triggered when menu action "layer" is clicked."""
        self.extent_layer_dialog.show()

    def on_action_selection_triggered(self):
        """Triggered when menu action "selection" is clicked."""
        self.prev_map_tool = self.canvas.mapTool()
        self.canvas.setMapTool(self.tool)
        self.dialog.showMinimized()

    def on_tool_update_extent(self):
        """Triggered when the map tool finishes drawing a rectangle."""
        rect = self.tool.rectangle()
        self.set_value_from_rect(rect)

        self.tool.reset()

        self.canvas.setMapTool(self.prev_map_tool)
        self.dialog.showNormal()
        self.dialog.raise_()
        self.dialog.activateWindow()

    def set_value_from_str(self, value, crs=None):
        """Set the coordinates from the coordinates string.

        If no CRS provided, gets the one from the project.
        There should be no CRS in the string!
        """
        # don't cache current project, as it may be changed
        crs = QgsProject.instance().crs() if not crs else crs

        if crs.isValid():
            value += ' [' + crs.authid() + ']'

        self.toggle_line_validity()
        self.lineEdit.setText(value)

    def set_value_from_layer(self, layer):
        """Set the coordinates to the passed layer extent."""
        self.set_value_from_rect(layer.extent(), layer.crs())

    def set_value_from_rect(self, rect, crs=None):
        """Set the coordinates from the passed rectangle extent.

        If no CRS provided, tries to obtain it from the rectangle.
        """
        value = rect.asWktCoordinates()
        crs = rect.crs() if isinstance(rect, QgsReferencedRectangle) else crs

        self.set_value_from_str(value, crs)
