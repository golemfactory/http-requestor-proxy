FROM python:3.8-slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /golem/work

VOLUME /golem/input /golem/output
