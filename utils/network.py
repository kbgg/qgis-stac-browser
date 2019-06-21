import ssl
import urllib
import shutil
import json
import os

def ssl_context():
    if os.environ.get('STAC_DEBUG', False):
        return ssl._create_unverified_context()
    return ssl.SSLContext()

def request(url, data=None):
    r = urllib.request.Request(url)
    if data is not None:
        body_bytes = json.dumps(data).encode('utf-8')
        r.add_header('Content-Type', 'application/json; charset=utf-8')
        r.add_header('Content-Length', len(body_bytes))
        r = urllib.request.urlopen(r, body_bytes, context=ssl_context(), timeout=5)
    else:
        r = urllib.request.urlopen(r, context=ssl_context(), timeout=5)

    return json.loads(r.read())

def download(url, path):
    with urllib.request.urlopen(url, context=ssl_context(), timeout=5) as response, open(path, 'wb') as f:
        shutil.copyfileobj(response, f)
