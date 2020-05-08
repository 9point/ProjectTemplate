# TODO: Rename this to RoutineEngine

import asyncio
import os
import torch

from utils.storage import s3_write

_PROJECT_NAME = os.environ.get('PROJECT_NAME')


class LocalRunEngine:
    def __init__(self, enable_storage=True):
        self.enable_storage = enable_storage
        self.run_loop = asyncio.new_event_loop()

    async def exec_task(self, task_exec, *args, **kwargs):
        if task_exec.is_coroutine:
            results = await task_exec.run(*args, **kwargs)
        else:
            results = task_exec.run(*args, **kwargs)

        # TODO: Need to store results based on the input parameters to the
        # task as well. May need the service's help with generating some
        # hash / identifier for the task, version, and input parameters.
        # if self.enable_storage:
        #     _write(task_exec, results)

        return results

    async def exec_workflow(self, wf_exec, *args, **kwargs):
        if wf_exec.is_coroutine:
            return await wf_exec.run(*args, **kwargs)
        else:
            return wf_exec.run(*args, **kwargs)


def _storage_path(task_exec):
    routine_id = task_exec.routine_id
    name = routine_id.routine_name
    version = routine_id.version

    assert(_PROJECT_NAME is not None)
    assert(name is not None)
    assert(version is not None)

    return f'projects/{_PROJECT_NAME}/{name}/{version}'


def _write(task_exec, obj):
    parent_path = _storage_path(task_exec)
    out_path = f'{parent_path}/out'
    meta_path = f'{parent_path}/meta'

    if isinstance(obj, torch.nn.Module):
        meta_type = f'torch:{torch.__version__}'
        with s3_write(out_path, 'b') as file:
            torch.save(obj.state_dict(), file)

        with s3_write(meta_path) as file:
            file.write(meta_type)

    else:
        raise TaskOutputStorageFailure()


class TaskOutputStorageFailure(Exception):
    pass
