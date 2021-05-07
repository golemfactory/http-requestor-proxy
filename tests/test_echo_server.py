from .sample_requests import sample_requests, BASE_URL
from .helpers import clean_headers, clean_body, send_request_to_quart_client

import pytest

from serializable_request import Request
from requests_flask_adapter import Session
import catchall_server
import echo_server
from unittest.mock import patch

Session.register(BASE_URL, catchall_server.app)

async def quart_client_forward():
    '''
    Replace yagna --> provider --> echo_server with echo_server used
    directly via requests_flask_adapter
    '''
    echo_url = 'http://echo/'
    Session.register(echo_url, echo_server.app)
    req = await Request.from_quart_request()
    req.replace_mount_url(echo_url)
    echo_res = Session().send(req.as_requests_request().prepare())
    return echo_res.content, echo_res.status_code, echo_res.headers.items()

@pytest.mark.asyncio
@pytest.mark.parametrize('src_req', sample_requests)
async def test_local_echo_server(src_req):
    prepped = src_req.prepare()
    
    client = catchall_server.app.test_client()

    with patch("catchall_server.forward_request", wraps=quart_client_forward):
        response = await send_request_to_quart_client(client, src_req, prepped)

    assert response.status_code == 200

    data = await response.json
    echo_req_data = data['req']

    echo_prepped = Request(**echo_req_data).as_requests_request().prepare()

    assert prepped.method == echo_prepped.method
    assert prepped.url == echo_prepped.url
    assert clean_headers(prepped.headers) == clean_headers(echo_prepped.headers)
    assert clean_body(prepped.body) == clean_body(echo_prepped.body)
