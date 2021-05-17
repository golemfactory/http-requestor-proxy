from quart import Quart
from yagna_connector import YagnaConnector
from serializable_request import Request

#   TODO: do we want to use hypercorn?
import hypercorn
hypercorn.Config.startup_timeout = 999

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

app = Quart(__name__)


@app.before_serving
async def start_provider():
    yagna = YagnaConnector()
    await yagna.init_provider()
    app.yagna = yagna


async def forward_request():
    req = await Request.from_quart_request()
    res = await app.yagna.process_request(req)
    return res.as_flask_response()


@app.route('/', defaults={'path': ''}, methods=HTTP_METHODS)
@app.route('/<path:path>', methods=HTTP_METHODS)
async def catch_all(path):
    res = await forward_request()
    return res

if __name__ == '__main__':
    app.run()
