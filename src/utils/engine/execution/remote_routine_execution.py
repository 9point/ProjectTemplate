import asyncio
import json

from . import create_local_run_id
from ..serializer import deserialize, serialize


class RemoteRoutineExecution:
    def __init__(self, connection, parent_run_id, executable, arguments):
        self.executable = executable
        self.local_run_id = create_local_run_id()
        self.arguments = arguments
        self.parent_run_id = parent_run_id
        self.run_id = None
        self._connection = connection
        self._event_loop = None
        self._fut = None

    @property
    def routine_id(self):
        return self.executable.routine_id

    async def __call__(self):
        loop = asyncio.get_running_loop()
        fut = loop.create_future()

        self._subs = [
            self._connection.on_directive('v1.routine.completed',
                                          self._on_routine_completed),
            self._connection.on_directive('v1.routine.starting',
                                          self._on_routine_starting),
            self._connection.on_directive('v1.routine.failed',
                                          self._on_routine_failed)
        ]

        arguments = serialize(self.arguments)
        request_payload = dict(localRunID=self.local_run_id,
                               parentRunID=self.parent_run_id,
                               routineID=str(self.executable.routine_id),
                               arguments=arguments)

        self._connection.send_directive(payload_key='v1.routine.request_start',
                                        payload=request_payload)

        self._event_loop = loop
        self._fut = fut

        return await fut

    def cleanup(self):
        if self._subs is not None:
            for s in self._subs:
                s()
            self._sub = None

        if self._fut is not None:
            self._fut.cancel()
            self._fut = None

    def _on_routine_starting(self, directive):
        if self._fut is None:
            return

        assert self._event_loop is not None

        assert 'localRunID' in directive.payload
        assert 'routineID' in directive.payload
        assert 'runID' in directive.payload

        if directive.payload['localRunID'] != self.local_run_id:
            # This routine is not the one run by this execution.
            return

        print('remote routine starting')

    def _on_routine_failed(self, directive):
        if self._fut is None:
            return

        assert self._event_loop is not None

        assert 'errorMessage' in directive.payload
        assert 'localRunID' in directive.payload
        assert 'routineID' in directive.payload
        assert 'runID' in directive.payload

        if directive.payload['localRunID'] != self.local_run_id:
            # This routine is not the one run by this execution.
            return

        self._event_loop.call_soon_threadsafe(self._fut.set_exception,
                                              RemoteExecutionFailed())

    def _on_routine_completed(self, directive):
        if self._fut is None:
            return

        assert self._event_loop is not None

        assert 'localRunID' in directive.payload
        assert 'result' in directive.payload
        assert 'routineID' in directive.payload
        assert 'runID' in directive.payload

        if directive.payload['localRunID'] != self.local_run_id:
            # This routine is not the one run by this execution.
            return

        result = deserialize(directive.payload['result'])
        self._event_loop.call_soon_threadsafe(self._fut.set_result,
                                              result)


class RemoteExecutionFailed(Exception):
    pass
