import click
from serializable_request import Request, Response
import requests_unixsocket


@click.command()
@click.option('--url', required=True)
@click.argument('req_fname')
@click.argument('res_fname')
def run(url, req_fname, res_fname):
    req = Request.from_file(req_fname)
    req.replace_mount_url('http://localhost/', url)
    print("URL", req.url)
    
    requests_req = req.as_requests_request()
    session = requests_unixsocket.Session()
    requests_res = session.send(requests_req.prepare())
    
    res = Response.from_requests_response(requests_res)
    res.to_file(res_fname)
    
    print(f"IN:  {req_fname}")
    print(f"OUT: {res_fname}")

if __name__ == '__main__':
    run()



