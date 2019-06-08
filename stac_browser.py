from PyQt5.QtCore import QSettings, QCoreApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction

from .resources import *
from .ui.collection_loading_dialog import CollectionLoadingDialog
from .ui.query_dialog import QueryDialog
from .ui.item_loading_dialog import ItemLoadingDialog
from .ui.results_dialog import ResultsDialog
import os.path

class STACBrowser:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        self.actions = []
        self.menu = u'&STAC Browser'

        self.current_window = 'COLLECTION_LOADING'
        self.windows = {
                    'COLLECTION_LOADING': {
                        'class': CollectionLoadingDialog,
                        'hooks': {'on_finished': self.collection_load_finished},
                        'data': None,
                        'dialog': None
                    },
                    'QUERY': { 
                        'class': QueryDialog,
                        'hooks': {'on_close': self.on_close, 'on_search': self.on_search},
                        'data': None,
                        'dialog': None
                    },
                    'ITEM_LOADING': { 
                        'class': ItemLoadingDialog,
                        'hooks': {'on_close': self.on_close, 'on_finished': self.item_load_finished},
                        'data': None,
                        'dialog': None
                    },
                    'RESULTS': { 
                        'class': ResultsDialog,
                        'hooks': {'on_close': self.on_close, 'on_back': self.on_back},
                        'data': None,
                        'dialog': None
                    },
                }

    def on_search(self, collections, extent_layer, time_period):
        (start_time, end_time) = time_period

        extent_rect = extent_layer.extent()
        extent = [extent_rect.xMinimum(), extent_rect.yMinimum(), extent_rect.xMaximum(), extent_rect.yMaximum()]

        self.windows['ITEM_LOADING']['data'] = { 
                    'collections': collections,
                    'extent': extent,
                    'start_time': start_time,
                    'end_time': end_time
                }
        self.current_window = 'ITEM_LOADING'
        self.windows['QUERY']['dialog'].close()
        self.load_window()

    def on_back(self):
        self.windows['RESULTS']['data'] = None
        self.windows['RESULTS']['dialog'].close()
        self.windows['RESULTS']['dialog'] = None

        self.current_window = 'QUERY'
        self.load_window()

    def on_close(self):
        for key, window in self.windows.items():
            if window['dialog'] is not None:
                window['dialog'].close()

            window['dialog'] = None
            window['data'] = None
        self.current_window = 'COLLECTION_LOADING'

    def load_window(self):
        window = self.windows.get(self.current_window, None)

        if window is None:
            print(f'Window {self.current_window} does not exist')
            return

        if window['dialog'] is None:
            window['dialog'] = window.get('class')(data=window.get('data'), hooks=window.get('hooks'))
            window['dialog'].show()
        else:
            window['dialog'].raise_()
            window['dialog'].show()
            window['dialog'].activateWindow()

    def reset_windows(self):
        for key, window in self.windows.items():
            window['data'] = None
            window['dialog'] = None

    def collection_load_finished(self, collections):
        collection_ids = []
        final_collections = []
        for collection in collections:
            if f'{collection.get_id()}:{collection.get_parent().get_url()}' in collection_ids:
                continue
            collection_ids.append(f'{collection.get_id()}:{collection.get_parent().get_url()}')
            final_collections.append(collection)
        self.windows['QUERY']['data'] = { 'collections': final_collections }
        self.current_window = 'QUERY'
        self.windows['COLLECTION_LOADING']['dialog'].close()
        self.load_window()

    def item_load_finished(self, items):
        self.windows['RESULTS']['data'] = { 'items': items }
        self.current_window = 'RESULTS'
        self.windows['ITEM_LOADING']['dialog'].close()
        self.windows['ITEM_LOADING']['data'] = None
        self.windows['ITEM_LOADING']['dialog'] = None
        self.load_window()

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        icon_path = ':/plugins/stac_browser/assets/icon.png'
        self.add_action(
            icon_path,
            text='Browse STAC Catalogs',
            callback=self.load_window,
            parent=self.iface.mainWindow())

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                u'&STAC Browser',
                action)
            self.iface.removeToolBarIcon(action)
