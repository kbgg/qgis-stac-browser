from .link import Link

class Collection:
    def __init__(self, api=None, json={}):
        self._api = api
        self._json = json

    @property
    def stac_version(self):
        return self._json.get('stac_version', None)

    @property
    def id(self):
        return self._json.get('id', None)

    @property
    def title(self):
        return self._json.get('title', None)

    @property
    def description(self):
        return self._json.get('description', None)

    @property
    def keywords(self):
        return self._json.get('keywords', [])

    @property
    def version(self):
        return self._json.get('version', None)

    @property
    def license(self):
        return self._json.get('license', None)

    @property
    def providers(self):
        return [Provider(p) for p in self._json.get('providers', [])]

    @property
    def extent(self):
        return Extent(self._json.get('extent', {}))

    @property
    def properties(self):
        return self._json.get('properties', [])

    @property
    def links(self):
        return [Link(l) for l in self._json.get('links', [])]

    @property
    def bands(self):
        bands = {}
        for i, band in enumerate(self.properties.get('eo:bands', [])):
            band['band'] = i+1
            bands[band.get('name', None)] = band

        return bands
    
    @property
    def api(self):
        return self._pi

    def __lt__(self, other):
        return self.title.lower() < other.title.lower()


class Extent:
    def __init__(self, json={}):
        self._json = json

    @property
    def spatial(self):
        return self._json.get('spatial', [])

    @property
    def temporal(self):
        return self._json.get('temporal', None)


class Provider:
    def __init__(self, json={}):
        self._json = json

    @property
    def name(self):
        return self._json.get('name', None)

    @property
    def description(self):
        return self._json.get('description', None)

    @property
    def roles(self):
        return self._json.get('roles', [])

    @property
    def url(self):
        return self._json.get('url', None)

