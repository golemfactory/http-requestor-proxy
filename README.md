# http-requestor-proxy
    
    #   Initialize
    python3 -m venv .venv
    . .venv/bin/activate
    pip install -r requirements.txt
    pip install pytest==6.2.3 pytest-asyncio==0.15.1

    #   Golem-free testing (golem-based tests are skipped)
    pytest

    #   Start golem-based service
    #   NOTE: it is assumed yagna requestor is initialized and running
    #   NOTE2: if the first task failed - for any reasony - manual restart is required,
    #          success is indicated by "[INFO] Application startup complete." message
    gunicorn catchall_server:app -b localhost:5000 -k uvicorn.workers.UvicornWorker
    
    #   Tests (~ 55 seconds)
    CATCHALL_SERVER_URL=http://localhost:5000 pytest tests/test_provider_echo_server.py 
