import requests


class Request():
    def __init__(self, method, url, data, headers):
        self.method = method
        self.url = url
        self.data = data
        self.headers = headers

    @classmethod
    def from_flask_request(cls):
        from flask import request
        return cls(request.method, request.url, request.get_data(), dict(request.headers))

    def as_requests_request(self):
        req = requests.Request(
            method=self.method,
            url=self.url,
            data=self.data,
            headers=self.headers,
        )
        return req
