#!/usr/bin/env python3

import requests_unixsocket
from requests import Request

fname = '/golem/output/ttt.txt'
url = 'http+unix://%2Ftmp%2Fgolem.sock/'

try:
    session = requests_unixsocket.Session()
    req = Request('get', url)
    res = session.send(req.prepare())
    msg = f"STATUS {res.status_code}"
except Exception as e:
    msg = f"ERROR {e}"

with open(fname, 'w') as f:
    f.write(msg)
