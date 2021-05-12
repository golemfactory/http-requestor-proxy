import asyncio

from tempfile import NamedTemporaryFile
from serializable_request import Request, Response
from datetime import timedelta

from yapapi import Executor, Task
from yapapi.log import enable_default_logger, log_summary, log_event_repr  # noqa
from yapapi.package import vm

from worker import worker


class YagnaConnector():
    def __init__(self):
        self.queue = asyncio.Queue()

    async def init_provider(self):
        enable_default_logger(
            log_file='log.log',
            debug_activity_api=True,
            # debug_market_api=True,
            # debug_payment_api=True,
        )
        asyncio.create_task(self._provider_startup())

        fut = asyncio.get_running_loop().create_future()
        self.queue.put_nowait(fut)

        await fut

        if fut.result() != {'status': 'STARTED'}:
            raise Exception(f'Failed to start provider: {fut.result()}')

    async def process_request(self, req: Request):
        with NamedTemporaryFile() as in_file, NamedTemporaryFile() as out_file:
            req.to_file(in_file.name)

            fut = asyncio.get_running_loop().create_future()
            data = ((in_file.name, out_file.name), fut)
            self.queue.put_nowait(data)

            await fut

            if fut.result() != {'status': 'SUCCESS'}:
                raise Exception(f'Failed to execute request: {fut.result()}')

            res = Response.from_file(out_file.name)

        return res

    async def _provider_startup(self):
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

            task = Task(data={'queue': self.queue})
            async for _ in executor.submit(worker, [task]):
                pass
