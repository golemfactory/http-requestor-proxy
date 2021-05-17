from urllib.parse import urlparse

def clean_quart_headers(headers):
    '''
    1. Lowercase http header names, we are case insensitive
    2. Remove headers added by Quart.test_client (used only for testing)
    '''
    out = dict(headers)
    out = {key.lower(): val for key, val in out.items()}

    quart_headers = {
        'user-agent': 'Quart',
        'remote-addr': '<local>',
        'host': 'localhost',
    }

    for key, val in quart_headers.items():
        if out.get(key, '') == val:
            del out[key]

    return out

def clean_requests_headers(headers, test_url):
    '''
    1. Remove headers added by python.requests
    2. Lowercase http header names, we are case insensitive
    '''
    out = dict(headers)
    out = {key.lower(): val for key, val in out.items()}

    requests_headers = {
        'accept-encoding': 'identity',
        'host': urlparse(test_url).netloc,
        'remote-addr': '127.0.0.1',
        'user-agent': 'python-urllib3/1.26.4'
    }

    for key, val in requests_headers.items():
        if out.get(key, '') == val:
            del out[key]

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

async def send_request_to_quart_client(client, req, prepped_req):
    '''
    client      - quart app.test_client()
    req         - tested request
    prepped_req - result of req.prepare() - we want to compare exactly the same prepped_req
                  with the results, and req.prepare().body != req.prepare().body, so
                  we can't prepare the request here
    '''
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
