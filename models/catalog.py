import requests
import json
import math
from .collection import Collection
from .item import Item

class Catalog:
    def __init__(self, url=None):
        self.url = url
        self.data = None

    def get_data(self):
        if self.data is None:
            return {}
        
        return self.data

    def get_title(self):
        return self.get_data().get('title', 'Unknown')

    def get_url(self):
        return self.url

    def get_collections(self):
        r = requests.get(f'{self.get_url()}/stac', verify=False)
        self.data = r.json()
        links = r.json().get('links', [])
        collections = []

        for link in links:
            if link.get('rel', None) == 'child':
                collection = Collection(parent=self, url=link.get('href', None))
                collections.append(collection)

        return collections

    def search_items(self, collections, extent, start_time, end_time, page=0, on_next_page=None):
        collection_ids = []
        items = []
        for collection in collections:
            collection_ids.append(collection.get_id())
        if on_next_page is not None: 
            on_next_page()
        r = requests.post(f'{self.get_url()}/stac/search',
                          json={
                              'collections': collection_ids,
                              'bbox': extent,
                              'page': page,
                              'limit': 100,
                              'time': f'{start_time.strftime("%Y-%m-%dT%H:%M:%SZ")}/{end_time.strftime("%Y-%m-%dT%H:%M:%SZ")}'
                              }, verify=False)
        data = r.json()
        for feature in data['features']:
           items.append(Item(data=feature)) 

        search_meta = data['meta']
        max_page = math.ceil(search_meta['found'] / search_meta['limit'])-1
        if page < max_page:
            more_items = self.search_items(collections, 
                                           extent, 
                                           start_time, 
                                           end_time, 
                                           page+1, 
                                           on_next_page=on_next_page)
            items.extend(more_items)

        return items
