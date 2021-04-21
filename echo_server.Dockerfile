#   TODO: change to -slim when development is finished
FROM python:3.8

WORKDIR /echo_server

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY golem_provider_mock.py  golem_provider_mock.py
COPY serializable_request.py serializable_request.py

COPY echo_server.py          echo_server.py

#   NOTE: second gunicorn is a mock of the final interface
CMD ["sh", "-c", "\
        gunicorn -b unix:///tmp/golem.sock echo_server:app --daemon; \
        gunicorn -b 0.0.0.0:8001 golem_provider_mock:app"]
