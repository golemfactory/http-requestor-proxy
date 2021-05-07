from urllib.parse import urlparse

def clean_headers(headers):
    '''
    1. Remove headers added by Quart.test_client (used only for testing)
    2. Lowercase http header names, we are case insensitive
    '''
    quart_headers = {
        'User-Agent': 'Quart',
        'Remote-Addr': '<local>',
        'Host': 'localhost',
    }
    out = dict(headers)
    for key, val in quart_headers.items():
        if out.get(key, '') == val:
            del out[key]

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
