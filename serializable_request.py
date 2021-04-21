import requests
import json


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

    @classmethod
    def from_file(cls, fname):
        with open(fname, 'r') as f:
            return cls.from_json(f.read())

    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json_data)
        return cls(
            data['method'],
            data['url'],
            data['data'].encode('utf-8'),
            data['headers'],
        )

    def to_file(self, fname):
        with open(fname, 'w') as f:
            f.write(self.as_json())

    def as_json(self):
        data = {
            'method': self.method,
            'url': self.url,
            'data': self.data.decode('utf-8'),
            'headers': self.headers,
        }
        return json.dumps(data)

    def as_requests_request(self):
        req = requests.Request(
            method=self.method,
            url=self.url,
            data=self.data,
            headers=self.headers,
        )
        return req
