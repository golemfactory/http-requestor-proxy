'''
Provider-side code goes here.
Everything Flask-related will be removed, but something similar to send_request_from_file will remain.

Some things here are ugly, but they will be replaced.
'''


from flask import Flask
from serializable_request import Request
from tempfile import NamedTemporaryFile
import requests_unixsocket

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']
app = Flask(__name__)


def send_request_from_file(fname):
    req = Request.from_file(fname)
    req.replace_mount_url('http://localhost/', 'http+unix://%2Ftmp%2Fgolem.sock/')
    session = requests_unixsocket.Session()
    return session.send(req.as_requests_request().prepare())


@app.route('/', defaults={'path': ''}, methods=HTTP_METHODS)
@app.route('/<path:path>', methods=HTTP_METHODS)
def catch_all(path):
    req = Request.from_flask_request()
    with NamedTemporaryFile() as f:
        req.to_file(f.name)
        res = send_request_from_file(f.name)
    return res.content, res.status_code, res.headers.items()
