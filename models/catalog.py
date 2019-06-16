from .link import Link

class Catalog:
    def __init__(self, api=None, json={}):
        self._api = api
        self._json = json
        self._collections = None

    @property
    def api(self):
        return self._api

    @property
    def id(self):
        return self._json.get('id', None)

    @property
    def stac_version(self):
        return self._json.get('stac_version', None)

    @property
    def title(self):
        return self._json.get('title', None)

    @property
    def description(self):
        return self._json.get('description', None)

    @property
    def collections(self):
        if self._collections is None:
            self.load_collections()

        return self._collections

    @property
    def links(self):
        return [Link(l) for l in self._json.get('links', [])]

    @property
    def api(self):
        return self._api

    def load_collections(self):
        self._collections = []
        for link in self.links:
            collection_id = self.api.collection_id_from_href(link.href)
            if collection_id is None:
                continue
            self._collections.append(self.api.load_collection(self, collection_id))

    def __lt__(self, other):
        return self.title.lower() < other.title.lower()

