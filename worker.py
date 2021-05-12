
from yapapi import WorkContext
from datetime import timedelta
from uuid import uuid4
from os import path

WORK_DIR = '/golem/work'
INPUT_DIR = '/golem/input'
OUTPUT_DIR = '/golem/output'

PROVIDER_SERVER_URL = 'unix:///tmp/golem.sock'

    
def start_server(ctx):
    for fname in ('serializable_request.py', 'echo_server.py', 'process_request.py'):
        ctx.send_file(fname, path.join(WORK_DIR, fname))
    ctx.run("/usr/local/bin/gunicorn", "-b", PROVIDER_SERVER_URL, "echo_server:app", "--daemon")

def make_request(ctx, src_data):
    local_in, local_out = src_data

    random_suffix = uuid4().hex
    remote_in = path.join(INPUT_DIR, f"req-{random_suffix}.json")
    remote_out = path.join(OUTPUT_DIR, f"res-{random_suffix}.json")

    ctx.send_file(local_in, remote_in)
    ctx.run('/usr/local/bin/python', '/golem/work/process_request.py',
            '--url', PROVIDER_SERVER_URL, remote_in, remote_out)
    ctx.download_file(remote_out, local_out)

async def worker(ctx: WorkContext, tasks):
    async for task in tasks:
        break
    queue = task.data['queue']
    
    start_server_fut = queue.get_nowait()
    start_server(ctx)
    yield ctx.commit(timeout=timedelta(10))
    start_server_fut.set_result({'status': 'STARTED'})

    while True:
        src_data, req_fut = await queue.get()
        make_request(ctx, src_data)
        yield ctx.commit(timeout=timedelta(10))
        req_fut.set_result({'status': 'SUCCESS'})
        queue.task_done()

    task.accept_result()
