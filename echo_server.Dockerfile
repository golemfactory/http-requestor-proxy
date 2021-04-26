#   TODO: change to -slim when development is finished
# FROM python:3.8
FROM golemfactory/blender:1.13

WORKDIR /golem/entrypoints/
COPY sample_run.py /golem/entrypoints/
COPY run-sample_run.sh /golem/entrypoints/

RUN chmod +x /golem/entrypoints/sample_run.py
RUN chmod +x /golem/entrypoints/run-sample_run.sh

VOLUME /golem/work /golem/input /golem/output

# COPY requirements.txt requirements.txt
# RUN pip install -r requirements.txt
# 
# COPY golem_provider_mock.py  golem_provider_mock.py
# COPY serializable_request.py serializable_request.py
# 
# COPY echo_server.py          echo_server.py
# 
# #   NOTE: second gunicorn is a mock of the final interface
# CMD ["sh", "-c", "\
#         gunicorn -b unix:///tmp/golem.sock echo_server:app --daemon; \
#         gunicorn -b 0.0.0.0:8001 golem_provider_mock:app"]
