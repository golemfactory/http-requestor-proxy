FROM python:3.8-slim

WORKDIR /echo_server

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY echo_server.py          echo_server.py
COPY serializable_request.py serializable_request.py

CMD gunicorn -b 0.0.0.0:8001 "echo_server:app"
