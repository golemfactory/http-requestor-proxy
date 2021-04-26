from .sample_requests import sample_requests, BASE_URL
from .helpers import clean_headers, clean_body

import pytest

from serializable_request import Request
from requests_flask_adapter import Session
import catchall_server
import echo_server
import os

Session.register(BASE_URL, catchall_server.app)


def requests_flask_adapter_url():
    echo_url = 'http://echo/'
    Session.register(echo_url, echo_server.app)
    return echo_url


def external_url():
    echo_url = os.environ.get('ECHO_SERVER_URL')
    if not echo_url:
        pytest.skip("ECHO_SERVER_URL is not set")
    return echo_url


def create_forward_func(echo_url):
    def forward():
        req = Request.from_flask_request()
        req.replace_mount_url(BASE_URL, echo_url)
        echo_res = Session().send(req.as_requests_request().prepare())
        return echo_res.content, echo_res.status_code, echo_res.headers.items()
    return forward


@pytest.mark.parametrize('get_url', [requests_flask_adapter_url, external_url])
@pytest.mark.parametrize('src_req', sample_requests)
def test_echo_server(get_url, src_req):
    url = get_url()
    catchall_server.forward_request = create_forward_func(url)
    prepped = src_req.prepare()

    res = Session().send(prepped)
    assert res.status_code == 200

    echo_req_data = res.json()['req']
    echo_prepped = Request(**echo_req_data).as_requests_request().prepare()

    assert prepped.method == echo_prepped.method
    assert prepped.url == echo_prepped.url
    assert clean_headers(prepped.headers) == clean_headers(echo_prepped.headers)
    assert clean_body(prepped.body) == clean_body(echo_prepped.body)
