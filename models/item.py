import os
import subprocess
import requests
import hashlib
import tempfile
from pathlib import Path

class Item:
    def __init__(self, catalog=None, json={}):
        self._catalog = catalog
        self._json = json

    @property
    def hashed_id(self):
        return hashlib.sha256(f'{self.catalog.api.href}/collections/{self.collection.id}/items/{self.id}'.encode('utf-8')).hexdigest()

    @property
    def catalog(self):
        return self._catalog

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
        assets = {}
        for key, d in self._json.get('assets', {}).items():
            assets[key] = Asset(d)

        return assets

    @property
    def collection(self):
        collection_id = self.properties.get('collection', None)
        if collection_id is None:
            collection_id = self._json.get('collection', None)

        for collection in self.catalog.collections:
            if collection.id == collection_id:
                return collection

        return None

    @property
    def thumbnail(self):
        return self.assets.get('thumbnail', None)

    @property
    def thumbnail_url(self):
        if self.thumbnail is None:
            return None

        return self.thumbnail.href

    @property
    def temp_dir(self):
        temp_dir = os.path.join(tempfile.gettempdir(), 'qgis-stac-browser', self.hashed_id)
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        return temp_dir

    @property
    def thumbnail_path(self):
        return os.path.join(self.temp_dir, 'thumbnail.jpg')

    @property
    def vrt(self):
        return os.path.join(self.temp_dir, 'asset.vrt')

    @property
    def bands(self):
        bands = []
        for k, band in self.collection.bands.items():
            asset = self.assets.get(k, None)
            if asset is not None:
                bands.append(asset)

        return bands

    def thumbnail_downloaded(self):
        return self._thumbnail is not None

    def download(self, bands, download_directory, stream=False, on_update=None):
        item_download_directory = os.path.join(download_directory, self.id)
        if not os.path.exists(item_download_directory):
            os.makedirs(item_download_directory)

        band_filenames = []
        for band in bands:
            asset = self.assets.get(band, None)

            if asset is None:
                print('!!! ASSET NOT FOUND !!!')
                continue

            if stream and asset.cog is not None:
                band_filenames.append(asset.cog)
                continue
            
            if on_update is not None:
                on_update('DOWNLOADING_BAND', data={'band': band, 'bands': bands})

            r = requests.get(asset.href)
            temp_filename = os.path.join(item_download_directory, asset.href.split('/')[-1])
            band_filenames.append(temp_filename)
            with open(temp_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    if chunk:
                        f.write(chunk)

        if on_update is not None:
            on_update('BUILDING_VRT', data={'bands': bands})
        arguments = ['gdalbuildvrt', '-separate', os.path.join(download_directory, f'{self.id}.vrt')]
        arguments.extend(band_filenames)
        subprocess.run(arguments)

    def __lt__(self, other):
        return self.id < other.id

class Asset:
    def __init__(self, json={}):
        self._json = json

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
    def type(self):
        return self._json.get('type', None)
