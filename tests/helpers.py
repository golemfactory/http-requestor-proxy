def clean_headers(headers):
    '''
    1. Remove headers added by request_flask_adapter (used only for testing)
    2. Lowercase http header names, we are case insensitive
    3. Remove 'accept-encoding': 'identity' header, added by http.client (deep inside requests)
       https://stackoverflow.com/a/18706328
    '''
    out = dict(headers)
    if out.get('User-Agent', '') == 'Quart':
        del out['User-Agent']
    if out.get('Remote-Addr', '') == '<local>':
        del out['Remote-Addr']
    if out.get('Host', '') == 'localhost':
        del out['Host']

    out = {key.lower(): val for key, val in out.items()}

    if out.get('accept-encoding', '') == 'identity':
        del out['accept-encoding']

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
