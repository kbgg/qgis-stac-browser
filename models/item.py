import os
from pathlib import Path

class Item:
    def __init__(self, data=None):
        self.data = data

    def get_data(self):
        if self.data is None:
            return {}

        return self.data

    def get_id(self):
        return self.get_data().get('id', 'N/A')

    def get_properties(self):
        return self.get_data().get('properties', {})

    def get_thumbnail_url(self):
        thumbnail = self.get_data().get('assets', {}).get('thumbnail', None)
        if thumbnail is None:
            return None
        return thumbnail.get('href', None)

    def get_temp_dir(self):
        return os.path.join(Path(__file__).parent.parent, 'tmp')

    def thumbnail_downloaded(self):
        return os.path.exists(self.get_thumbnail_path())

    def get_thumbnail_path(self):
        if not os.path.exists(self.get_temp_dir()):
            os.makedirs(self.get_temp_dir())
        previews_dir = os.path.join(self.get_temp_dir(), 'previews')

        if not os.path.exists(previews_dir):
            os.makedirs(previews_dir)
        path = os.path.join(previews_dir, self.get_id())

        return path

    def asset_downloaded(self):
        return os.path.exists(self.get_asset_path())

    def get_asset_path(self):
        if not os.path.exists(self.get_temp_dir()):
            os.makedirs(self.get_temp_dir())
        assets_dir = os.path.join(self.get_temp_dir(), 'assets')

        if not os.path.exists(assets_dir):
            os.makedirs(assets_dir)
        path = os.path.join(assets_dir, self.get_id())

        return path

    def download(self):
        pass

    def __lt__(self, other):
        return self.get_id() < other.get_id()
