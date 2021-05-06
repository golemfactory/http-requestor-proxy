#!/usr/bin/env python3
from datetime import datetime, timedelta
from asgiref.sync import async_to_sync
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

def init_echo_server(ctx):
    for fname in ('serializable_request.py', 'echo_server.py', 'process_request.py'):
        ctx.send_file(fname, path.join(WORK_DIR, fname))
    ctx.run("/usr/local/bin/gunicorn", "-b", PROVIDER_SERVER_URL, "echo_server:app", "--daemon")


def make_request(ctx, request_ix):
    our_in = 'req.json'
    our_out = 'res.json'

    random_prefix = uuid4().hex
    their_in = path.join(INPUT_DIR, random_prefix + our_in)
    their_out = path.join(OUTPUT_DIR, random_prefix + our_out)

    ctx.send_file(our_in, their_in)
    ctx.run('/usr/local/bin/python', '/golem/work/process_request.py',
            '--url', PROVIDER_SERVER_URL, their_in, their_out)
    ctx.download_file(their_out, our_out)
    return our_out


async def main(subnet_tag='devnet-beta.1'):
    package = await vm.repo(
        image_hash="332f8937d0995471c756d46ee8bea6712ca780fadb55bdb216ac70af",
        min_mem_gib=0.5,
        min_storage_gib=2.0,
    )

    async def worker(ctx: WorkContext, tasks):
        init_echo_server(ctx)
        files = []
        async for task in tasks:
            for i in range(1):
                new_file = make_request(ctx, i)
                files.append(new_file)
                yield ctx.commit(timeout=timedelta(seconds=1200))
            task.accept_result(result=files)

    async with Executor(
        package=package,
        max_workers=3,
        budget=1.0,
        timeout=timedelta(minutes=30),
        subnet_tag=subnet_tag,
        event_consumer=log_summary(log_event_repr),
    ) as executor:

        print(
            f"Using subnet: {subnet_tag}, "
            f"payment driver: {executor.driver}, "
            f"and network: {executor.network}\n"
        )

        num_tasks = 0
        start_time = datetime.now()

        async for task in executor.submit(worker, [Task(data={'some': 'data'})]):
            num_tasks += 1
            print(f"Task computed: {task}, result: {task.result}, time: {task.running_time}")

        print(f"{num_tasks} tasks computed, total time: {datetime.now() - start_time}")


@async_to_sync
async def sync_main():
    await main()

if __name__ == "__main__":
    enable_default_logger(
        log_file='log.log',
        debug_activity_api=True,
        # debug_market_api=True,
        # debug_payment_api=True,
    )
    sync_main()
