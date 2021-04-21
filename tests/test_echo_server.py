from .sample_requests import sample_requests, BASE_URL
from .helpers import clean_headers, clean_body

import pytest

from serializable_request import Request
from requests_flask_adapter import Session
import catchall_server
import echo_server

ECHO_URL = 'http://echo/'
Session.register(BASE_URL, catchall_server.app)
Session.register(ECHO_URL, echo_server.app)


def request_flask_adapter_forward():
    req = Request.from_flask_request()
    req.url = req.url.replace(BASE_URL, ECHO_URL)
    echo_res = Session().send(req.as_requests_request().prepare())
    return echo_res.content, echo_res.status_code, echo_res.headers.items()


@pytest.mark.parametrize('forward_func', [request_flask_adapter_forward])
@pytest.mark.parametrize('src_req', sample_requests)
def test_echo_server(forward_func, src_req):
    catchall_server.forward_request = forward_func
    prepped = src_req.prepare()

    res = Session().send(prepped)
    assert res.status_code == 200

    echo_req_data = res.json()['req']
    echo_prepped = Request(**echo_req_data).as_requests_request().prepare()

    assert prepped.method == echo_prepped.method
    assert prepped.url == echo_prepped.url
    assert clean_headers(prepped.headers) == clean_headers(echo_prepped.headers)
    assert clean_body(prepped.body) == clean_body(echo_prepped.body)
