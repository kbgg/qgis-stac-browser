import ssl
import urllib
import shutil
import json

def request(url, data=None):
    context = ssl._create_unverified_context()
    r = urllib.request.Request(url)
    if data is not None:
        body_bytes = json.dumps(data).encode('utf-8')
        r.add_header('Content-Type', 'application/json; charset=utf-8')
        r.add_header('Content-Length', len(body_bytes))
        r = urllib.request.urlopen(r, body_bytes, context=context)
    else:
        r = urllib.request.urlopen(r, context=context)
    return json.loads(r.read())

def download(url, path):
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(url, context=context) as response, open(path, 'wb') as f:
        shutil.copyfileobj(response, f)
