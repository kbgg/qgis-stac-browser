from PyQt5 import uic, QtWidgets

from ..utils import ui


FORM_CLASS, _ = uic.loadUiType(ui.path('about_dialog.ui'))


class AboutDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, path=None, parent=None, iface=None):
        super(AboutDialog, self).__init__(parent)
        self.iface = iface

        self.setupUi(self)

        if path is not None:
            with open(path, 'r') as f:
                contents = f.read()
            self.textBrowser.setHtml(contents)

        self.closeButton.clicked.connect(self.on_close_clicked)

    def on_close_clicked(self):
        self.reject()
