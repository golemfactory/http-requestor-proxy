from .sample_requests import sample_requests, BASE_URL
from .helpers import clean_headers, clean_body
from yagna_connector import YagnaConnector

import pytest

from serializable_request import Request, Response
from requests_flask_adapter import Session
import catchall_server
import echo_server
import os

Session.register(BASE_URL, catchall_server.app)

#   TODO
#   currently previous test influence subsequent ones
#   --> setup_* functions should be context managers
#   --> use (maybe?) mock.patch.object
#   (this is harmless now because of the order of parametrizations in main testing func)


def setup_local_forward():
    echo_url = 'http://echo/'
    Session.register(echo_url, echo_server.app)

    def local_forward():
        req = Request.from_flask_request()
        req.replace_mount_url(echo_url)
        echo_res = Session().send(req.as_requests_request().prepare())
        return echo_res.content, echo_res.status_code, echo_res.headers.items()
    catchall_server.forward_request = local_forward


def setup_container_forward():
    echo_url = os.environ.get('ECHO_SERVER_URL')
    if not echo_url:
        pytest.skip("ECHO_SERVER_URL is not set")

    def yagna_run_request(self, req_fname, res_fname):
        '''
        INT: file name with serialized request
        OUT: file name with serialized response
        '''
        req = Request.from_file(req_fname)
        req.replace_mount_url(echo_url)
        requests_res = Session().send(req.as_requests_request().prepare())
        res = Response.from_requests_response(requests_res)
        res.to_file(res_fname)

    YagnaConnector.run_request = yagna_run_request


@pytest.mark.parametrize('src_req', sample_requests)
@pytest.mark.parametrize('setup_func', [setup_container_forward, setup_local_forward])
def test_local_echo_server(setup_func, src_req):
    setup_func()
    prepped = src_req.prepare()

    res = Session().send(prepped)
    assert res.status_code == 200

    echo_req_data = res.json()['req']
    echo_prepped = Request(**echo_req_data).as_requests_request().prepare()

    assert prepped.method == echo_prepped.method
    assert prepped.url == echo_prepped.url
    assert clean_headers(prepped.headers) == clean_headers(echo_prepped.headers)
    assert clean_body(prepped.body) == clean_body(echo_prepped.body)
