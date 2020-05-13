import asyncio
import queue
import threading

from .execution.local_routine_execution import LocalRoutineExecution
from .execution.remote_routine_execution import RemoteRoutineExecution
from .serializer import deserialize, serialize


class RemoteDispatchEngine:
    def __init__(self, connection):
        self._connection = connection
        self._loop = None
        self._result_queue = queue.Queue()
        self._work_queue = queue.Queue()

    @property
    def status(self):
        return self._status

    @property
    def result_queue(self):
        return self._result_queue

    def schedule_executable(self, executable, *args, **kwargs):
        execution = LocalRoutineExecution(executable, *args, **kwargs)
        self._work_queue.put(execution)

    def start(self):
        """
        Starts the engine. This method does not return (unless there is
        a major engine error).
        """
        assert self._loop is None

        self._loop = asyncio.new_event_loop()
        self._main_task = self._loop.create_task(self._start())
        self._loop.run_forever()

    def stop(self):
        # TODO: IMPLEMENT ME!
        assert(False, 'RemoteDispatchEngine has not yet implemented stop')

    async def _start(self):
        while True:
            self._status = 'IDLE'
            execution = self._work_queue.get(block=True)
            self._status = 'WORKING'
            result = await execution()
            self._result_queue.put((execution, result))

    async def run_executable(self, executable, *args, **kwargs):
        assert self._loop is not None

        self._status = 'HANGING'
        execution = LocalRoutineExecution(executable, *args, **kwargs)
        result = await execution()

        self._status = 'WORKING'
        return result
