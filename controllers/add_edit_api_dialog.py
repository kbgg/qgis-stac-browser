import uuid
import urllib

from PyQt5 import uic, QtWidgets

from ..utils import ui
from ..utils.logging import error

from ..threads.load_api_data_thread import LoadAPIDataThread
from ..models.api import API

FORM_CLASS, _ = uic.loadUiType(ui.path('add_edit_api_dialog.ui'))


class AddEditAPIDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, data={}, hooks={}, parent=None, iface=None):
        super(AddEditAPIDialog, self).__init__(parent)

        self.data = data
        self.hooks = hooks
        self.iface = iface

        self.setupUi(self)

        self.populate_details()
        self.populate_auth_method_combo()

        self.cancelButton.clicked.connect(self.on_cancel_clicked)
        self.removeButton.clicked.connect(self.on_remove_clicked)
        self.saveAddButton.clicked.connect(self.on_save_add_clicked)

    def on_cancel_clicked(self):
        self.reject()

    def on_remove_clicked(self):
        self.hooks['remove_api'](self.api)
        self.accept()

    def set_all_enabled(self, enabled):
        self.urlEditBox.setEnabled(enabled)
        self.authenticationCombo.setEnabled(enabled)
        self.removeButton.setEnabled(enabled)
        self.cancelButton.setEnabled(enabled)
        self.saveAddButton.setEnabled(enabled)

    def on_save_add_clicked(self):
        self.set_all_enabled(False)
        self.saveAddButton.setText('Testing Connection...')

        api_id = str(uuid.uuid4())
        if self.api is not None:
            api_id = self.api.id

        api = API({'id': api_id, 'href': self.urlEditBox.text()})
        self.loading_thread = LoadAPIDataThread(
            api,
            on_error=self.on_api_error,
            on_finished=self.on_api_success)
        self.loading_thread.start()

    def on_api_error(self, e):
        self.set_all_enabled(True)
        if self.api is None:
            self.saveAddButton.setText('Add')
        else:
            self.saveAddButton.setText('Save')

        if type(e) == urllib.error.URLError:
            error(self.iface, f'Connection Failed; {e.reason}')
        else:
            error(self.iface, f'Connection Failed; {type(e).__name__}')

    def on_api_success(self, api):
        if self.api is None:
            self.hooks['add_api'](api)
        else:
            self.hooks['edit_api'](api)
        self.accept()

    @property
    def api(self):
        return self.data.get('api', None)

    def populate_details(self):
        if self.api is None:
            self.saveAddButton.setText('Add')
            self.removeButton.hide()
            return

        self.urlEditBox.setText(self.api.href)

    def populate_auth_method_combo(self):
        self.authenticationCombo.addItem('No Auth')
