import click
from serializable_request import Request, Response
import requests_unixsocket


@click.command()
@click.option('--url', required=True)
@click.argument('req_fname')
@click.argument('res_fname')
def run(url, req_fname, res_fname):
    url = _adjust_url(url)

    req = Request.from_file(req_fname)
    req.replace_mount_url(url)
    
    requests_req = req.as_requests_request()
    session = requests_unixsocket.Session()
    requests_res = session.send(requests_req.prepare())
    
    res = Response.from_requests_response(requests_res)
    res.to_file(res_fname)
    
    print(f"IN:  {req_fname}")
    print(f"OUT: {res_fname}")

def _adjust_url(url):
    '''
    Only current usecase:
        unix:///tmp/golem.sock/  --> http+unix://%2Ftmp%2Fgolem.sock
        
    NOTE: urllib.parse is not used, because it doesn't work well with urls with empty host,
          e.g. with the one above
    '''
    if '://' not in url:
        raise ValueError(f"Missing schema in url {url}")

    schema, no_schema_url = url.split('://', 1)
    if schema == 'unix':
        #   This is required by requests_unixsocket
        schema = 'http+unix'

    if no_schema_url.endswith('/'):
        no_schema_url = no_schema_url[:-1]

    if no_schema_url.startswith('/'):
        #   If this is a no-host url, and we don't url-encode all '/',
        #   requests assume the path is the host.
        #   Also we can't use ullib.parse.quote, because some part might
        #   already be url-encoded.
        no_schema_url = no_schema_url.replace('/', '%2F')
    
    return '://'.join([schema, no_schema_url])


if __name__ == '__main__':
    run()
