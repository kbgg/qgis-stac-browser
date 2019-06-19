import os
import json

class Config:
    STAC_APIS = ['https://stac.boundlessgeo.io', 'https://sat-api.developmentseed.org']

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
                    'apis': self.apis
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
            apis = self.STAC_APIS

        return apis 
