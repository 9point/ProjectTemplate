import asyncio
import threading

from uuid import uuid4
from .execution.local_routine_execution import LocalRoutineExecution


class LocalRunEngine:
    def __init__(self, connection):
        self._connection = connection
        self._loop = None
        self._status = 'IDLE'

    @property
    def status(self):
        return self._status

    def start_executable(self, run_id, executable, arguments):
        assert self._loop is None

        execution = LocalRoutineExecution(run_id, executable, arguments)

        self._loop = asyncio.new_event_loop()
        future = self._loop.create_task(execution())
        self._status = 'WORKING'
        result = self._loop.run_until_complete(future)
        self._status = 'IDLE'

        return result

    def stop(self):
        # TODO: IMPLEMENT ME!
        pass

    async def run_executable(self, executable, *args, **kwargs):
        assert self._loop is not None

        run_id = uuid4()
        arguments = dict(args=args, kwargs=kwargs)
        execution = LocalRoutineExecution(run_id, executable, arguments)
        return await execution()
