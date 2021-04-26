#!/usr/bin/env python3
from datetime import datetime, timedelta
from asgiref.sync import async_to_sync
import pathlib

from yapapi import (
    Executor,
    Task,
    WorkContext,
)
from yapapi.log import enable_default_logger, log_summary, log_event_repr  # noqa
from yapapi.package import vm


async def main(subnet_tag='devnet-beta.1'):
    package = await vm.repo(
        image_hash="9a3b5d67b0b27746283cb5f287c13eab1beaa12d92a9f536b747c7ae",
        min_mem_gib=0.5,
        min_storage_gib=2.0,
    )

    async def worker(ctx: WorkContext, tasks):
        script_dir = pathlib.Path(__file__).resolve().parent
        scene_path = str(script_dir / "cubes.blend")
        ctx.send_file(scene_path, "/golem/resource/scene.blend")
        async for task in tasks:
            frame = task.data
            crops = [{"outfilebasename": "out", "borders_x": [0.0, 1.0], "borders_y": [0.0, 1.0]}]
            ctx.send_json(
                "/golem/work/params.json",
                {
                    "scene_file": "/golem/resource/scene.blend",
                    "resolution": (400, 300),
                    "use_compositing": False,
                    "crops": crops,
                    "samples": 100,
                    "frames": [frame],
                    "output_format": "PNG",
                    "RESOURCES_DIR": "/golem/resources",
                    "WORK_DIR": "/golem/work",
                    "OUTPUT_DIR": "/golem/output",
                },
            )
            for i in range(2):
                ctx.run("/golem/entrypoints/run-blender.sh")
                output_file = f"output_{frame}_{i}.png"
                ctx.download_file(f"/golem/output/out{frame:04d}.png", output_file)
                yield ctx.commit(timeout=timedelta(seconds=120))
            task.accept_result(result=output_file)

    # Iterator over the frame indices that we want to render
    frames: range = [0, 10]

    # By passing `event_consumer=log_summary()` we enable summary logging.
    # See the documentation of the `yapapi.log` module on how to set
    # the level of detail and format of the logged information.
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

        async for task in executor.submit(worker, [Task(data=frame) for frame in frames]):
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
        debug_market_api=True,
        debug_payment_api=True,
    )
    sync_main()
