# http-requestor-proxy

    python3 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements.txt
    docker build . -f echo_server.Dockerfile -t echo_server
    docker run -d -p "8001:8001" --name echo_server echo_server
    ECHO_SERVER_URL="http://localhost:8001/" pytest
    docker stop echo_server
