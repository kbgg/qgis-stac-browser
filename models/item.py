import os
import subprocess
import hashlib
import tempfile
from ..utils import network
from ..models.link import Link


class Item:
    def __init__(self, api=None, json={}):
        self._api = api
        self._json = json

    @property
    def hashed_id(self):
        return hashlib.sha256(
            f'{self.api.href}/collections/{self.collection.id}/items/{self.id}'
            .encode('utf-8')
        ).hexdigest()

    @property
    def api(self):
        return self._api

    @property
    def id(self):
        return self._json.get('id', None)

    @property
    def type(self):
        return self._json.get('type', None)

    @property
    def geometry(self):
        return self._json.get('geometry', None)

    @property
    def bbox(self):
        return self._json.get('bbox', None)

    @property
    def properties(self):
        return self._json.get('properties', {})

    @property
    def links(self):
        return [Link(l) for l in self._json.get('links', [])]

    @property
    def assets(self):
        assets = []
        for key, d in self._json.get('assets', {}).items():
            assets.append(Asset(key, d, item=self))

        return assets

    @property
    def collection(self):
        collection_id = self.properties.get('collection', None)
        if collection_id is None:
            collection_id = self._json.get('collection', None)

        for collection in self.api.collections:
            if collection.id == collection_id:
                return collection

        return None

    @property
    def thumbnail(self):
        for asset in self.assets:
            if asset.key == 'thumbnail':
                return asset
        return None

    @property
    def thumbnail_url(self):
        if self.thumbnail is None:
            return None

        return self.thumbnail.href

    @property
    def temp_dir(self):
        temp_dir = os.path.join(
            tempfile.gettempdir(),
            'qgis-stac-browser',
            self.hashed_id
        )
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        return temp_dir

    @property
    def thumbnail_path(self):
        return os.path.join(self.temp_dir, 'thumbnail.jpg')

    def thumbnail_downloaded(self):
        return self._thumbnail is not None

    def download_steps(self, options):
        steps = 0

        for asset_key in options.get('assets', []):
            for asset in self.assets:
                if asset.key != asset_key:
                    continue

                if options.get('stream_cogs', False) and asset.cog is not None:
                    continue

                steps += 1

        if options.get('add_to_layers', False):
            steps += 1
        return steps

    def download(self, gdal_path, options, download_directory, on_update=None):
        item_download_directory = os.path.join(download_directory, self.id)
        if not os.path.exists(item_download_directory):
            os.makedirs(item_download_directory)

        raster_filenames = []

        for asset_key in options.get('assets', []):
            for asset in self.assets:
                if asset.key != asset_key:
                    continue

                if options.get('stream_cogs', False) and asset.cog is not None:
                    raster_filenames.append(asset.cog)
                    continue

                if on_update is not None:
                    on_update(f'Downloading {asset.href}')

                temp_filename = os.path.join(
                    item_download_directory,
                    asset.href.split('/')[-1]
                )
                if asset.is_raster:
                    raster_filenames.append(temp_filename)
                network.download(asset.href, temp_filename)

        if options.get('add_to_layers', False):
            if on_update is not None:
                on_update(f'Building Virtual Raster...')

            arguments = [
                os.path.join(gdal_path, 'gdalbuildvrt'),
                '-separate',
                os.path.join(download_directory, f'{self.id}.vrt')
            ]
            arguments.extend(raster_filenames)
            subprocess.run(arguments)

    def __lt__(self, other):
        return self.id < other.id


class Asset:
    def __init__(self, key, json={}, item=None):
        self._key = key
        self._json = json
        self._item = item

    @property
    def is_raster(self):
        return (self._json.get('eo:name', None) is not None)

    @property
    def key(self):
        return self._key

    @property
    def cog(self):
        if self.type in ['image/x.geotiff', 'image/vnd.stac.geotiff']:
            return f'/vsicurl/{self.href}'

        return None

    @property
    def href(self):
        return self._json.get('href', None)

    @property
    def title(self):
        return self._json.get('title', None)

    @property
    def pretty_title(self):
        if self.title is not None:
            return self.title

        return self.key

    @property
    def type(self):
        return self._json.get('type', None)

    @property
    def band(self):
        if self._item.collection is None:
            return -1

        collection_bands = self._item.collection.properties.get('eo:bands', [])

        for i, c in enumerate(collection_bands):
            if c.get('name', None) == self.key:
                return i

        return -1

    def __lt__(self, other):
        if self.band != -1 and other.band != -1:
            return self.band < other.band

        if self.band == -1 and other.band != -1:
            return False

        if self.band != -1 and other.band == -1:
            return True

        if self.title is None or other.title is None:
            return self.key.lower() < other.key.lower()

        return self.title.lower() < other.title.lower()
