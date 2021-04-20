from flask import Flask

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']
app = Flask(__name__)


def forward_request():
    raise NotImplementedError


@app.route('/', defaults={'path': ''}, methods=HTTP_METHODS)
@app.route('/<path:path>', methods=HTTP_METHODS)
def catch_all(path):
    res = forward_request()
    return res
