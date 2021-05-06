from tempfile import NamedTemporaryFile
from serializable_request import Request, Response
from asgiref.sync import async_to_sync
from datetime import timedelta
from uuid import uuid4

from yapapi import (
    Executor,
    Task,
    WorkContext,
)
from yapapi.log import enable_default_logger, log_summary, log_event_repr  # noqa
from yapapi.package import vm

from os import path

WORK_DIR = '/golem/work'
INPUT_DIR = '/golem/input'
OUTPUT_DIR = '/golem/output'

PROVIDER_SERVER_URL = 'unix:///tmp/golem.sock'

async def worker(ctx: WorkContext, tasks):
    def prepare_server():
        for fname in ('serializable_request.py', 'echo_server.py', 'process_request.py'):
            ctx.send_file(fname, path.join(WORK_DIR, fname))
        ctx.run("/usr/local/bin/gunicorn", "-b", PROVIDER_SERVER_URL, "echo_server:app", "--daemon")

    def make_request(our_in, our_out):
        random_suffix = uuid4().hex
        their_in = path.join(INPUT_DIR, f"req-{random_suffix}.json")
        their_out = path.join(OUTPUT_DIR, f"res-{random_suffix}.json")
    
        ctx.send_file(our_in, their_in)
        ctx.run('/usr/local/bin/python', '/golem/work/process_request.py',
                '--url', PROVIDER_SERVER_URL, their_in, their_out)
        ctx.download_file(their_out, our_out)
        
    prepare_server()
    async for task in tasks:
        in_fname, out_fname = task.data['in_fname'], task.data['out_fname']
        make_request(in_fname, out_fname)
        yield ctx.commit(timeout=timedelta(seconds=1200))
        task.accept_result(result=out_fname)

class YagnaConnector():
    def __init__(self):
        enable_default_logger(
            log_file='log.log',
            debug_activity_api=True,
            debug_market_api=True,
            debug_payment_api=True,
        )

    def process_request(self, req: Request):
        with NamedTemporaryFile() as in_file, NamedTemporaryFile() as out_file:
            req.to_file(in_file.name)
            self._run_request(in_file.name, out_file.name)
            res = Response.from_file(out_file.name)
        return res
    

    @async_to_sync
    async def _run_request(self, in_fname, out_fname):
        package = await vm.repo(
            image_hash="332f8937d0995471c756d46ee8bea6712ca780fadb55bdb216ac70af",
            min_mem_gib=0.5,
            min_storage_gib=2.0,
        )
        async with Executor(
            package=package,
            max_workers=1,
            budget=1.0,
            timeout=timedelta(minutes=30),
            subnet_tag='devnet-beta.1',
            event_consumer=log_summary(log_event_repr),
        ) as executor:
            print(
                "Using subnet: 'devnet-beta.1, "
                f"payment driver: {executor.driver}, "
                f"and network: {executor.network}\n"
            )

            task_data = {'in_fname': in_fname, 'out_fname': out_fname}
            async for task in executor.submit(worker, [Task(data=task_data)]):
                print(f"Task computed: {task}, result: {task.result}, time: {task.running_time}")
    
