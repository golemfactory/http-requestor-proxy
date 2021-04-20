from .sample_requests import sample_requests, BASE_URL

import pytest

from requests_flask_adapter import Session
import catchall_server
from pytest import fixture
from engine import Request

out_req = None


@fixture
def session():
    Session.register(BASE_URL, catchall_server.app)
    return Session()


def pseudo_forward_1():
    '''
    Send request.
    Recreate request from flask internal context.
    '''
    global out_req
    out_req = Request.from_flask_request().as_requests_request()
    return {}, 200


def pseudo_forward_2():
    '''
    Send request.
    Recreate request from flask internal context.
    Save request to file.
    Read request from the file.
    '''
    raise NotImplementedError


def clean_headers(headers):
    '''
    1. Remove headers added by request_flask_adapter (used only for testing)
    2. Lowercase header names, we are case insensitive
    '''
    out = dict(headers)
    if out.get('User-Agent', '') == 'RequestsFlask/0.0.1':
        del out['User-Agent']
    if out.get('Host', '') == 'localhost':
        del out['Host']

    out = {key.lower(): val for key, val in out.items()}
    return out


def clean_body(body):
    '''
    I don't know why, but prepped.body is sometimes str (should be bytes).
    Maybe a bug in requests?
    I consider this to be a testing-only issue.
    '''
    if type(body) is str:
        return body.encode('UTF-8')
    return body


@pytest.mark.parametrize('forward_func', [pseudo_forward_1])
@pytest.mark.parametrize('src_req', sample_requests)
def test_request(forward_func, session, src_req):
    catchall_server.forward_request = forward_func
    prepped = src_req.prepare()

    res = session.send(prepped)
    assert res.status_code == 200

    out_prepped = out_req.prepare()
    assert prepped.method == out_prepped.method
    assert prepped.url == out_prepped.url
    assert clean_headers(prepped.headers) == clean_headers(out_prepped.headers)
    assert clean_body(prepped.body) == clean_body(out_prepped.body)
