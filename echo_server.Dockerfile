#   TODO: change to -slim when development is finished
FROM python:3.8

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /golem/entrypoints/
COPY sample_request.py /golem/entrypoints/
RUN chmod +x /golem/entrypoints/sample_request.py

VOLUME /golem/work /golem/input /golem/output

COPY serializable_request.py serializable_request.py
COPY echo_server.py          echo_server.py

ENTRYPOINT ["gunicorn", "-b", "unix:///tmp/golem.sock", "echo_server:app"]
