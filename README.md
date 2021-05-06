# http-requestor-proxy
    
    #   Golem-free testing
    python3 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements.txt
    pip install pytest=6.2.3
    gunicorn -b 0.0.0.0:5000 "echo_server:app" --daemon
    
    ECHO_SERVER_URL=http://localhost:5000 pytest
    pkill gunicorn

    #   Run on provider (assuming yagna requestor is ready)
    python3 requestor.py

    #   Success: res.json file, with response to req.json
