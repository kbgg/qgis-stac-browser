import os
import json
from ..models.api import API


class Config:
    def __init__(self):
        self._json = None
        self.load()

    def load(self):
        if not os.path.exists(self.path):
            self._json = {}
            self.save()
        else:
            with open(self.path, 'r') as f:
                self._json = json.load(f)

    def save(self):
        config = {
            'apis': [api.json for api in self.apis],
            'download_directory': self.download_directory,
            'last_update': self.last_update,
            'api_update_interval': self.api_update_interval
        }
        with open(self.path, 'w') as f:
            f.write(json.dumps(config))

    @property
    def path(self):
        return os.path.join(
            os.path.split(os.path.dirname(__file__))[0],
            'config.json'
        )

    @property
    def apis(self):
        apis = self._json.get('apis', None)

        if apis is None:
            apis = [
                {
                    "id": "default-staccato",
                    "href": "https://stac.boundlessgeo.io",
                },
                {
                    "id": "default-sat-api",
                    "href": "https://sat-api.developmentseed.org",
                },
                {
                    "id": "default-astraea",
                    "href": "https://stac.astraea.earth/api/v2",
                }
            ]

        return [API(api) for api in apis]

    @apis.setter
    def apis(self, apis):
        self._json['apis'] = [api.json for api in apis]

    @property
    def last_update(self):
        return self._json.get('last_update', None)

    @property
    def api_update_interval(self):
        return self._json.get('api_update_interval', 60 * 60 * 24)

    @last_update.setter
    def last_update(self, value):
        self._json['last_update'] = value

    @property
    def download_directory(self):
        if self._json.get('download_directory', None) is None:
            return os.environ.get('HOME', '')
        return self._json.get('download_directory', '')

    @download_directory.setter
    def download_directory(self, value):
        self._json['download_directory'] = value
