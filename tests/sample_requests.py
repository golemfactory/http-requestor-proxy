from requests import Request
from urllib.parse import urljoin

BASE_URL = 'http://localhost/'

sample_requests = [
    Request('get', BASE_URL),
    Request('post', urljoin(BASE_URL, 'aaa/zz')),
    Request('post', urljoin(BASE_URL, 'aaa/zz'), data={'foo': 'bar'}),
]
