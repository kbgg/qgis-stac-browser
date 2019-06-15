import requests
import re
from urllib.parse import urlparse
from .collection import Collection
from .catalog import Catalog
from .search_result import SearchResult

class API:
    VERIFY_SSL = False

    def __init__(self, href=None):
        self._href = href
        self._catalog = None

    def load_catalog(self):
        r = requests.get(f'{self.href}/stac', verify=self.VERIFY_SSL)
        return Catalog(self, r.json())

    def load_collection(self, catalog, collection_id):
        r = requests.get(f'{self.href}/collections/{collection_id}', verify=self.VERIFY_SSL)
        return Collection(catalog, r.json())

    def search_items(self, collections=[], bbox=[], start_time=None,
                     end_time=None, page=1, limit=50, on_next_page=None):
        if on_next_page is not None:
            on_next_page()

        if end_time is None:
            time = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            time = f'{start_time.strftime("%Y-%m-%dT%H:%M:%SZ")}/{end_time.strftime("%Y-%m-%dT%H:%M:%SZ")}'

        r = requests.post(f'{self.href}/stac/search',
                json = {
                        'collections': [c.id for c in collections],
                        'bbox': bbox,
                        'time': time,
                        'page': page,
                        'limit': limit
                    }, verify=self.VERIFY_SSL)


        search_result = SearchResult(self, r.json())
        
        items = search_result.items
        if len(items) >= limit:
            items.extend(self.search_items(collections, bbox, start_time, end_time, page+1, limit, on_next_page=on_next_page))

        return items
     
    def collection_id_from_href(self, href):
        p = re.compile('\/collections\/(.*)')
        m = p.match(urlparse(href).path)
        if m is None:
            return None

        if m.groups() is None:
            return None

        return m.groups()[0]

    @property
    def href(self):
        return self._href
    
    @property
    def catalog(self):
        if self._catalog is None:
            self._catalog = self.load_catalog()

        return self._catalog

