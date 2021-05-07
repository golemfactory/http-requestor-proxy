from .sample_requests import sample_requests
from .helpers import clean_requests_headers, clean_body

import pytest

from serializable_request import Request
import os
from requests import Session

@pytest.mark.parametrize('src_req', sample_requests)
def test_on_provider(src_req):
    '''Test a real scenario, with echo_server running on provider'''
    catchall_server_url = os.environ.get('CATCHALL_SERVER_URL', '')
    if not catchall_server_url:
        pytest.skip()

    src_req.url = catchall_server_url
    prepped = src_req.prepare()

    response = Session().send(prepped)

    assert response.status_code == 200

    echo_req_data = response.json()['req']

    echo_prepped = Request(**echo_req_data).as_requests_request().prepare()

    assert prepped.method == echo_prepped.method
    assert prepped.url == echo_prepped.url
    assert clean_requests_headers(prepped.headers, catchall_server_url) == \
           clean_requests_headers(echo_prepped.headers, catchall_server_url)
    assert clean_body(prepped.body) == clean_body(echo_prepped.body)
