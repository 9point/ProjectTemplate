import asyncio
import queue
import sys
import threading

from .executable.task_executable import TaskExecutable
from .execution.local_routine_execution import LocalRoutineExecution
from .execution.remote_routine_execution import RemoteRoutineExecution
from .serializer import deserialize, serialize


class RemoteDispatchEngine:
    def __init__(self, connection):
        self._connection = connection
        self._loop = None
        self._result_queue = queue.Queue()
        self._task_queue = queue.Queue()
        self._execution_context = threading.local()

    @property
    def status(self):
        return self._status

    @property
    def result_queue(self):
        return self._result_queue

    def schedule_executable(self, executable, run_id, arguments):
        if isinstance(executable, TaskExecutable):
            self._schedule_task_executable(executable, run_id, arguments)
        else:
            self._schedule_workflow_executable(executable, run_id, arguments)

    def _schedule_workflow_executable(self, executable, run_id, arguments):
        execution = LocalRoutineExecution(executable, run_id, arguments)
        workflow_loop = asyncio.new_event_loop()
        thread = threading.Thread(target=self._run_workflow,
                                  args=(workflow_loop, execution, self._result_queue))
        thread.start()

    def _schedule_task_executable(self, executable, run_id, arguments):
        execution = LocalRoutineExecution(executable, run_id, arguments)
        self._task_queue.put(execution)

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
            execution = self._task_queue.get(block=True)
            self._status = 'WORKING'

            self._execution_context.parent_run_id = execution.run_id
            result = await execution()
            execution.cleanup()
            self._result_queue.put((execution, result))

    def _run_workflow(self, event_loop, execution, result_queue):
        print('running workflow')

        async def run(fut, execution, result_queue):
            self._execution_context.parent_run_id = execution.run_id
            try:
                result = await execution()
            except:
                execution.cleanup()
                fut.set_exception(sys.exc_info()[0])
            else:
                fut.set_result(result)

        fut = event_loop.create_future()
        event_loop.create_task(run(fut, execution, result_queue))
        result = event_loop.run_until_complete(fut)
        execution.cleanup()
        result_queue.put((execution, result))

    async def run_executable(self, executable, *args, **kwargs):
        parent_run_id = getattr(self._execution_context, 'parent_run_id', None)

        assert self._loop is not None
        assert parent_run_id is not None

        arguments = dict(args=args, kwargs=kwargs)

        # TODO: When there is an exception here, the thread silently
        # fails. Need to look into this.
        execution = RemoteRoutineExecution(self._connection,
                                           parent_run_id,
                                           executable,
                                           arguments)

        result = await execution()

        execution.cleanup()
        return result
