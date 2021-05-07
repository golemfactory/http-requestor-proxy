from quart import Quart


HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

app = Quart(__name__)


async def forward_request():
    raise NotImplementedError

@app.route('/', defaults={'path': ''}, methods=HTTP_METHODS)
@app.route('/<path:path>', methods=HTTP_METHODS)
async def catch_all(path):
    res = await forward_request()
    return res
