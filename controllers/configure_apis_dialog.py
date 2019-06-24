from PyQt5 import uic, QtWidgets

from ..utils import ui
from ..utils.config import Config

from ..controllers.add_edit_api_dialog import AddEditAPIDialog


FORM_CLASS, _ = uic.loadUiType(ui.path('configure_apis_dialog.ui'))


class ConfigureAPIDialog(QtWidgets.QDialog, FORM_CLASS):
    def __init__(self, data={}, hooks={}, parent=None, iface=None):
        super(ConfigureAPIDialog, self).__init__(parent)

        self.data = data
        self.hooks = hooks
        self.iface = iface

        self.setupUi(self)

        self.populate_api_list()
        self.populate_api_details()

        self.list.activated.connect(self.on_list_clicked)

        self.apiAddButton.clicked.connect(self.on_add_api_clicked)
        self.apiEditButton.clicked.connect(self.on_edit_api_clicked)
        self.closeButton.clicked.connect(self.on_close_clicked)

    def on_close_clicked(self):
        self.reject()

    def on_add_api_clicked(self):
        dialog = AddEditAPIDialog(
            data={'api': None},
            hooks={
                "remove_api": self.remove_api,
                "add_api": self.add_api,
                "edit_api": self.edit_api
            },
            parent=self,
            iface=self.iface
        )
        dialog.exec_()

    def on_edit_api_clicked(self):
        dialog = AddEditAPIDialog(
            data={'api': self.selected_api},
            hooks={
                "remove_api": self.remove_api,
                "add_api": self.add_api,
                "edit_api": self.edit_api
            },
            parent=self,
            iface=self.iface
        )
        dialog.exec_()

    def edit_api(self, api):
        config = Config()
        new_apis = []

        for a in config.apis:
            if a.id == api.id:
                continue
            new_apis.append(a)
        new_apis.append(api)
        config.apis = new_apis
        config.save()

        self.data['apis'] = config.apis
        self.populate_api_list()
        self.populate_api_details()

    def add_api(self, api):
        config = Config()
        apis = config.apis
        apis.append(api)
        config.apis = apis
        config.save()

        self.data['apis'] = config.apis
        self.populate_api_list()
        self.populate_api_details()

    def remove_api(self, api):
        config = Config()
        new_apis = []

        for a in config.apis:
            if a.id == api.id:
                continue
            new_apis.append(a)

        config.apis = new_apis
        config.save()

        self.data['apis'] = config.apis
        self.populate_api_list()
        self.populate_api_details()

    def populate_api_list(self):
        self.list.clear()
        for api in self.apis:
            api_node = QtWidgets.QListWidgetItem(self.list)
            api_node.setText(f'{api.title}')

    def populate_api_details(self):
        if self.selected_api is None:
            self.apiUrlLabel.hide()
            self.apiUrlValue.hide()
            self.apiTitleLabel.hide()
            self.apiTitleValue.hide()
            self.apiVersionLabel.hide()
            self.apiVersionValue.hide()
            self.apiDescriptionLabel.hide()
            self.apiDescriptionValue.hide()
            self.apiEditButton.hide()
            return

        self.apiUrlValue.setText(self.selected_api.href)
        self.apiTitleValue.setText(self.selected_api.title)
        self.apiVersionValue.setText(self.selected_api.version)
        self.apiDescriptionValue.setText(self.selected_api.description)

        self.apiUrlLabel.show()
        self.apiUrlValue.show()
        self.apiTitleLabel.show()
        self.apiTitleValue.show()
        self.apiVersionLabel.show()
        self.apiVersionValue.show()
        self.apiDescriptionLabel.show()
        self.apiDescriptionValue.show()
        self.apiEditButton.show()

    @property
    def apis(self):
        return self.data.get('apis', [])

    @property
    def selected_api(self):
        items = self.list.selectedIndexes()
        for i in items:
            return self.apis[i.row()]
        return None

    def on_list_clicked(self):
        self.populate_api_details()
