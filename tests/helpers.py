def clean_headers(headers):
    '''
    1. Remove headers added by request_flask_adapter (used only for testing)
    2. Lowercase http header names, we are case insensitive
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
