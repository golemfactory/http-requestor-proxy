#!/usr/bin/env python3
from datetime import datetime, timedelta
from asgiref.sync import async_to_sync

from yapapi import (
    Executor,
    Task,
    WorkContext,
)
from yapapi.log import enable_default_logger, log_summary, log_event_repr  # noqa
from yapapi.package import vm


async def main(subnet_tag='devnet-beta.1'):
    package = await vm.repo(
        image_hash="ab2a4af2d7ed13d29f08a7c725a7bff3ec05f82a77e0394f5e91bc55",
        min_mem_gib=0.5,
        min_storage_gib=2.0,
    )

    async def worker(ctx: WorkContext, tasks):
        async for task in tasks:
            for i in range(2):
                their_file, our_file = "/golem/output/ttt.txt", f"output_{i}.txt"
                ctx.run("/golem/entrypoints/sample_request.py")
                ctx.download_file(their_file, our_file)
                yield ctx.commit(timeout=timedelta(seconds=1200))
            task.accept_result(result=our_file)

    async with Executor(
        package=package,
        max_workers=3,
        budget=10.0,
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
