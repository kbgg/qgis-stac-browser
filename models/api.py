import re
from urllib.parse import urlparse
from .collection import Collection
from .catalog import Catalog
from .search_result import SearchResult
from ..utils import network

class API: 
    def __init__(self, href=None):
        self._href = href
        self._catalog = None

    def load_catalog(self):
        return Catalog(self, network.request(f'{self.href}/stac'))

    def load_collection(self, catalog, collection_id):
        return Collection(catalog, network.request(f'{self.href}/collections/{collection_id}'))

    def search_items(self, collections=[], bbox=[], start_time=None,
                     end_time=None, page=1, limit=50, on_next_page=None):
        if on_next_page is not None:
            on_next_page()

        if end_time is None:
            time = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        else:
            time = f'{start_time.strftime("%Y-%m-%dT%H:%M:%SZ")}/{end_time.strftime("%Y-%m-%dT%H:%M:%SZ")}'

        body = {
                    'collections': [c.id for c in collections],
                    'bbox': bbox,
                    'time': time,
                    'page': page,
                    'limit': limit
               }

        search_result = SearchResult(self, network.request(f'{self.href}/stac/search', data=body))
        
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

