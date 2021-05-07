from .sample_requests import sample_requests, BASE_URL
from .helpers import clean_headers, clean_body

import pytest

from serializable_request import Request
from requests_flask_adapter import Session
import catchall_server
import echo_server
from urllib.parse import urlparse

Session.register(BASE_URL, catchall_server.app)

#   TODO
#   currently previous test influence subsequent ones
#   --> setup_* functions should be context managers
#   --> use (maybe?) mock.patch.object
#   (this is harmless now because of the order of parametrizations in main testing func)


def setup_local_forward():
    echo_url = 'http://echo/'
    Session.register(echo_url, echo_server.app)

    async def local_forward():
        req = await Request.from_quart_request()
        req.replace_mount_url(echo_url)
        echo_res = Session().send(req.as_requests_request().prepare())
        return echo_res.content, echo_res.status_code, echo_res.headers.items()
    catchall_server.forward_request = local_forward

async def send_request_to_quart_client(req, prepped_req):
    client = catchall_server.app.test_client()

    path = urlparse(req.url).path
    headers = dict(prepped_req.headers)
    
    async with client.request(path, query_string=req.params, method=req.method, headers=headers) as connection:
        body = prepped_req.body
        if body is not None:
            if type(body) is str:
                body = body.encode('utf-8')
            await connection.send(body)
        await connection.send_complete()
    response = await connection.as_response()
    return response

@pytest.mark.asyncio
@pytest.mark.parametrize('src_req', sample_requests)
@pytest.mark.parametrize('setup_func', [setup_local_forward])
async def test_local_echo_server(setup_func, src_req):
    setup_func()
    prepped = src_req.prepare()
    
    response = await send_request_to_quart_client(src_req, prepped)
    assert response.status_code == 200

    data = await response.json
    echo_req_data = data['req']

    echo_prepped = Request(**echo_req_data).as_requests_request().prepare()

    assert prepped.method == echo_prepped.method
    assert prepped.url == echo_prepped.url
    assert clean_headers(prepped.headers) == clean_headers(echo_prepped.headers)
    assert clean_body(prepped.body) == clean_body(echo_prepped.body)
