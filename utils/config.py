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
                    'apis': [api.json for api in self.apis]
                }
        with open(self.path, 'w') as f:
            f.write(json.dumps(config))

    @property
    def path(self):
        return os.path.join(os.path.split(os.path.dirname(__file__))[0], 'config.json')

    @property
    def apis(self):
        apis = self._json.get('apis', None)

        if apis is None:
            apis = [
                        {
                            "href": "https://stac.boundlessgeo.io",
                        },
                        {
                            "href": "https://sat-api.developmentseed.org",
                        },
                        {
                            "href": "https://stac.astraea.earth/api/v2",
                        }
                    ]

        return [API(api) for api in apis]
