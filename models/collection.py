import requests
import urllib.parse as urlparse
import math
from .item import Item

class Collection:
    def __init__(self, parent=None, url=None):
        self.parent = parent
        self.url = url
        self.data = None

    def get_url(self):
        return self.url

    def get_parent(self):
        return self.parent

    def get_search_url(self):
        return f'{self.get_url()}/items'

    def load(self):
        r = requests.get(self.get_url(), verify=False)
        self.data = r.json()

    def get_data(self):
        if self.data is None:
            return {}

        return self.data

    def get_title(self):
        return self.get_data().get('title', 'Unknown')

    def get_id(self):
        return self.get_data().get('id', 'N/A')

    def __lt__(self, other):
        return self.get_title() < other.get_title()
