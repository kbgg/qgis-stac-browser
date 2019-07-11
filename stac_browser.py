import time
import os.path
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction

from .resources import *
from .controllers.collection_loading_dialog import CollectionLoadingDialog
from .controllers.query_dialog import QueryDialog
from .controllers.item_loading_dialog import ItemLoadingDialog
from .controllers.results_dialog import ResultsDialog
from .controllers.downloading_controller import DownloadController
from .controllers.download_selection_dialog import DownloadSelectionDialog
from .controllers.configure_apis_dialog import ConfigureAPIDialog
from .controllers.about_dialog import AboutDialog
from .utils.config import Config
from .utils.logging import error
from .utils import crs


class STACBrowser:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        self.actions = []
        self.application = None
        self.menu = u'&STAC Browser'

        self.current_window = 'COLLECTION_LOADING'

        self.windows = {
            'COLLECTION_LOADING': {
                'class': CollectionLoadingDialog,
                'hooks': {
                    'on_finished': self.collection_load_finished,
                    'on_close': self.on_close
                },
                'data': None,
                'dialog': None
            },
            'QUERY': {
                'class': QueryDialog,
                'hooks': {
                    'on_close': self.on_close,
                    'on_search': self.on_search
                },
                'data': None,
                'dialog': None
            },
            'ITEM_LOADING': {
                'class': ItemLoadingDialog,
                'hooks': {
                    'on_close': self.on_close,
                    'on_finished': self.item_load_finished,
                    'on_error': self.results_error
                },
                'data': None,
                'dialog': None
            },
            'RESULTS': {
                'class': ResultsDialog,
                'hooks': {
                    'on_close': self.on_close,
                    'on_back': self.on_back,
                    'on_download': self.on_download,
                    'select_downloads': self.select_downloads
                },
                'data': None,
                'dialog': None
            },
        }

    def on_search(self, api_collections, extent_rect, time_period, query):
        (start_time, end_time) = time_period

        # the API consumes only EPSG:4326
        extent_rect = crs.transform(extent_rect.crs(), 4326, extent_rect)

        extent = [
            extent_rect.xMinimum(),
            extent_rect.yMinimum(),
            extent_rect.xMaximum(),
            extent_rect.yMaximum()
        ]

        self.windows['ITEM_LOADING']['data'] = {
            'api_collections': api_collections,
            'extent': extent,
            'start_time': start_time,
            'end_time': end_time,
            'query': query,
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
        if self.windows is None:
            return
        self.reset_windows()

    def on_download(self, download_items, download_directory):
        self._download_controller = DownloadController(
            data={
                'downloads': download_items,
                'download_directory': download_directory,
            },
            hooks={},
            iface=self.iface
        )
        self.reset_windows()

    def downloading_finished(self):
        self.windows['DOWNLOADING']['dialog'].close()
        self.current_window = 'COLLECTION_LOADING'
        self.reset_windows()

    def collection_load_finished(self, apis):
        self.windows['QUERY']['data'] = {'apis': apis}
        self.current_window = 'QUERY'
        self.windows['COLLECTION_LOADING']['dialog'].close()
        self.load_window()

    def results_error(self):
        self.windows['ITEM_LOADING']['dialog'].close()
        self.windows['ITEM_LOADING']['dialog'] = None
        self.windows['ITEM_LOADING']['data'] = None
        self.current_window = 'QUERY'
        self.load_window()

    def item_load_finished(self, items):
        self.windows['RESULTS']['data'] = {'items': items}
        self.current_window = 'RESULTS'
        self.windows['ITEM_LOADING']['dialog'].close()
        self.windows['ITEM_LOADING']['data'] = None
        self.windows['ITEM_LOADING']['dialog'] = None
        self.load_window()

    def select_downloads(self, items, download_directory):
        dialog = DownloadSelectionDialog(
            data={'items': items},
            hooks={'on_close': self.on_close},
            parent=self.windows['RESULTS']['dialog']
        )

        result = dialog.exec_()

        if not result:
            return

        self.on_download(dialog.downloads, download_directory)

    def add_action(self, icon_path, text, callback, enabled_flag=True,
                   add_to_menu=True, add_to_toolbar=True, status_tip=None,
                   whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(self.menu, action)

        self.actions.append(action)

        return action

    def load_window(self):
        correct_version = self.check_version()
        if not correct_version:
            return
        if self.current_window == 'COLLECTION_LOADING':
            config = Config()
            if config.last_update is not None \
                    and time.time() - config.last_update \
                    < config.api_update_interval:
                self.current_window = 'QUERY'
                self.windows['QUERY']['data'] = {'apis': config.apis}

        window = self.windows.get(self.current_window, None)

        if window is None:
            error(self.iface, f'Window {self.current_window} does not exist')
            return

        if window['dialog'] is None:
            window['dialog'] = window.get('class')(
                data=window.get('data'),
                hooks=window.get('hooks'),
                parent=self.iface.mainWindow(),
                iface=self.iface
            )
            window['dialog'].show()
        else:
            window['dialog'].raise_()
            window['dialog'].show()
            window['dialog'].activateWindow()

    def reset_windows(self):
        for key, window in self.windows.items():
            if window['dialog'] is not None:
                window['dialog'].close()
            window['data'] = None
            window['dialog'] = None
        self.current_window = 'COLLECTION_LOADING'

    def check_version(self):
        if sys.version_info < (3, 6):
            v = '.'.join((
                str(sys.version_info.major),
                str(sys.version_info.minor),
                str(sys.version_info.micro)
            ))
            error(
                self.iface,
                ''.join((
                    'This plugin requires Python >= 3.6; ',
                    f'You are running {v}'
                ))
            )
            return False
        return True

    def configure_apis(self):
        correct_version = self.check_version()
        if not correct_version:
            return
        dialog = ConfigureAPIDialog(
            data={'apis': Config().apis},
            hooks={},
            parent=self.iface.mainWindow(),
            iface=self.iface
        )
        dialog.exec_()

    def about(self):
        dialog = AboutDialog(
            os.path.join(self.plugin_dir, 'about.html'),
            parent=self.iface.mainWindow(),
            iface=self.iface
        )
        dialog.exec_()

    def initGui(self):
        icon_path = ':/plugins/stac_browser/assets/icon.png'
        self.add_action(
            icon_path,
            text='Browse STAC Catalogs',
            callback=self.load_window,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/stac_browser/assets/cog.svg'
        self.add_action(
            icon_path,
            text='Configure APIs',
            add_to_toolbar=False,
            callback=self.configure_apis,
            parent=self.iface.mainWindow())

        icon_path = ':/plugins/stac_browser/assets/info.svg'
        self.add_action(
            icon_path,
            text='About',
            add_to_toolbar=False,
            callback=self.about,
            parent=self.iface.mainWindow())

    def unload(self):
        for action in self.actions:
            self.iface.removePluginWebMenu(u'&STAC Browser', action)
            self.iface.removeToolBarIcon(action)
