import pytest
from requests_flask_adapter import Session
from .sample_requests import sample_requests, BASE_URL
from .helpers import clean_headers, clean_body
from serializable_request import Request

import catchall_server

Session.register(BASE_URL, catchall_server.app)

@pytest.mark.parametrize('src_req', sample_requests)
def test_provider_run(src_req):
    prepped = src_req.prepare()

    res = Session().send(prepped)
    assert res.status_code == 200

    echo_req_data = res.json()['req']
    echo_prepped = Request(**echo_req_data).as_requests_request().prepare()

    assert prepped.method == echo_prepped.method
    assert prepped.url == echo_prepped.url
    assert clean_headers(prepped.headers) == clean_headers(echo_prepped.headers)
    assert clean_body(prepped.body) == clean_body(echo_prepped.body)
