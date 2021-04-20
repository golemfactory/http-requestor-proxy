import requests


class Request():
    def __init__(self, method, url):
        self.method = method
        self.url = url

    @classmethod
    def from_flask_request(cls):
        from flask import request
        return cls(request.method, request.url)

    @classmethod
    def from_requests_request(cls, request):
        return cls(request.method, request.url)

    def as_requests_request(self):
        req = requests.Request(
            self.method,
            self.url,
        )
        return req

    def __eq__(self, other):
        return type(self) == type(other) and \
                self.url == other.url and \
                self.method.lower() == other.method.lower()

    def __repr__(self):
        return f'{self.method}({self.url})'
