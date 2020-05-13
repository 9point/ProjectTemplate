import asyncio

from . import create_execution_id
from ..serializer import deserialize, serialize


class RemoteRoutineExecution:
    def __init__(self, connection, executable, *args, **kwargs):
        self.executable = executable
        self.local_id = create_execution_id()
        self.arguments = dict(args=args, kwargs=kwargs)
        self._connection = connection
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
        request_payload = dict(requestingWorkerLocalExecutionID=self.local_id,
                               routine_id=self.executable.routine_id,
                               arguments=arguments)

        self._connection.send_directive(payload_key='v1.routine.request_start',
                                        payload=request_payload)

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

        assert 'requestingWorkerLocalExecutionID' in directive.payload

        if directive.payload['requestingWorkerLocalExecutionID'] != self.local_id:
            # This routine is not the one run by this execution.
            return

        print('routine starting')

    def _on_routine_failed(self, directive):
        if self._fut is None:
            return

        assert 'requestingWorkerLocalExecutionID' in directive.payload

        if directive.payload['requestingWorkerLocalExecutionID'] != self.local_id:
            # This routine is not the one run by this execution.
            return

        print('routine failed')

    def _on_routine_completed(self, directive):
        if self._fut is None:
            return

        assert 'requestingWorkerLocalExecutionID' in directive.payload

        if directive.payload['requestingWorkerLocalExecutionID'] != self.local_id:
            # This routine is not the one run by this execution.
            return

        assert 'result' in directive.payload

        result = deserialize(directive.payload['result'])
        self._fut.set_result(result)
