from flask import Flask
from serializable_request import Request
from yagna_connector import YagnaConnector


HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']


yagna_connector = YagnaConnector()
app = Flask(__name__)


def forward_request():
    req = Request.from_flask_request()
    res = yagna_connector.process_request(req)
    return res.as_flask_response()


@app.route('/', defaults={'path': ''}, methods=HTTP_METHODS)
@app.route('/<path:path>', methods=HTTP_METHODS)
def catch_all(path):
    res = forward_request()
    return res
