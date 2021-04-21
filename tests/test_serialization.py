from .sample_requests import sample_requests, BASE_URL
from .helpers import clean_headers, clean_body

import pytest

from requests_flask_adapter import Session
import catchall_server
from pytest import fixture
from engine import Request
from tempfile import NamedTemporaryFile

out_req = None


@fixture
def session():
    Session.register(BASE_URL, catchall_server.app)
    return Session()


def pseudo_forward():
    '''
    Send request to flask.
    Recreate request using flask internal request context.

    This tests if we use flask.request correctly.
    '''
    global out_req
    out_req = Request.from_flask_request().as_requests_request()
    return {}, 200


def pseudo_forward_with_file():
    '''
    Send request.
    Recreate request from flask internal request context.
    Save request to file.
    Read request from this file.

    Assuming pseudo_forward finds no errors, this tests if we correctly
    serialize/deserialize the request.
    '''
    global out_req
    req = Request.from_flask_request()

    with NamedTemporaryFile() as f:
        req.to_file(f.name)
        out_req = Request.from_file(f.name).as_requests_request()
    return {}, 200


@pytest.mark.parametrize('forward_func', [pseudo_forward, pseudo_forward_with_file])
@pytest.mark.parametrize('src_req', sample_requests)
def test_serialization(forward_func, session, src_req):
    catchall_server.forward_request = forward_func
    prepped = src_req.prepare()

    res = session.send(prepped)
    assert res.status_code == 200

    out_prepped = out_req.prepare()
    assert prepped.method == out_prepped.method
    assert prepped.url == out_prepped.url
    assert clean_headers(prepped.headers) == clean_headers(out_prepped.headers)
    assert clean_body(prepped.body) == clean_body(out_prepped.body)
