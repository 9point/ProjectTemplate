import asyncio
import threading

from .execution.local_routine_execution import LocalRoutineExecution
from .execution.remote_routine_execution import RemoteRoutineExecution
from .serializer import deserialize, serialize


class RemoteDispatchEngine:
    def __init__(self, connection):
        self._connection = connection
        self._executions = []
        self._loop = None
        self._future_registry = {}

    def start(self, executable, *args, **kwargs):
        assert self._loop is None
        # TODO: IMPLEMENT ME! START THE LOOP.

    def cleanup(self):
        # TODO: IMPLEMENT ME!
        pass

    def run_executable(self, executable, *args, **kwargs):
        assert self._loop is not None
        return await self._remote_execution(executable, *args, **kwargs)

    def _local_execution(self, executable, *args, **kwargs):
        execution = LocalRoutineExecution(executable)
        return await execution

    def _remote_execution(self, executable, *args, **kwargs):
        execution = RemoteRoutineExecution(self._connection, executable)
        self._executions.append(execution)

        result = await execution(*args, **kwargs)

        execution.cleanup()

        return result
