from .sample_requests import sample_requests, BASE_URL
from .helpers import clean_headers, clean_body

import pytest
from requests_flask_adapter import Session
from tempfile import NamedTemporaryFile

import catchall_server
from serializable_request import Request

Session.register(BASE_URL, catchall_server.app)


def extract_request():
    return Request.from_flask_request().as_requests_request()


def extract_and_serialize():
    '''
    Assuming extract_request finds no errors, this tests if we correctly
    serialize/deserialize the request.
    '''
    req = Request.from_flask_request()

    with NamedTemporaryFile() as f:
        req.to_file(f.name)
        return Request.from_file(f.name).as_requests_request()


def process_request(extract_func, prepped):
    out_req = None

    def pseudo_forward_func():
        nonlocal out_req
        out_req = extract_func()
        return {}, 200

    catchall_server.forward_request = pseudo_forward_func

    res = Session().send(prepped)
    return res, out_req


@pytest.mark.parametrize('extract_func', [extract_request, extract_and_serialize])
@pytest.mark.parametrize('src_req', sample_requests)
def test_serialization(extract_func, src_req):
    prepped = src_req.prepare()

    res, out_req = process_request(extract_func, prepped)
    out_prepped = out_req.prepare()

    #   Fail --> traceback in serialization
    assert res.status_code == 200

    #   Fail --> incorrect serialization
    assert prepped.method == out_prepped.method
    assert prepped.url == out_prepped.url
    assert clean_headers(prepped.headers) == clean_headers(out_prepped.headers)
    assert clean_body(prepped.body) == clean_body(out_prepped.body)
