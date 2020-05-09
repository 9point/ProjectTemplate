import asyncio
import threading

from .execution.local_routine_execution import LocalRoutineExecution


class LocalRunEngine:
    def __init__(self):
        self._loop = None

    def start(self, executable, *args, **kwargs):
        assert self._loop is None

        execution = LocalRoutineExecution(executable)

        self._loop = asyncio.new_event_loop()
        future = self._loop.create_task(execution(*args, **kwargs))
        result = self._loop.run_until_complete(future)

        return result

    def stop(self):
        # TODO: IMPLEMENT ME!
        pass

    async def run_executable(self, executable, *args, **kwargs):
        assert self._loop is not None

        execution = LocalRoutineExecution(executable)
        return await execution(*args, **kwargs)
