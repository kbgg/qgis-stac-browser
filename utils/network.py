import ssl
import urllib
import shutil
import json
import os

def request(url, data=None):
    if os.environ.get('STAC_DEBUG', False):
        context = ssl._create_unverified_context()
    else:
        context = None

    r = urllib.request.Request(url)
    if data is not None:
        body_bytes = json.dumps(data).encode('utf-8')
        r.add_header('Content-Type', 'application/json; charset=utf-8')
        r.add_header('Content-Length', len(body_bytes))
        r = urllib.request.urlopen(r, body_bytes, context=context, timeout=5)
    else:
        r = urllib.request.urlopen(r, context=context, timeout=5)

    return json.loads(r.read())

def download(url, path):
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(url, context=context, timeout=5) as response, open(path, 'wb') as f:
        shutil.copyfileobj(response, f)
