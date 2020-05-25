import asyncio
import queue
import sys
import threading

from .executable.task_executable import TaskExecutable
from .execution.local_routine_execution import LocalRoutineExecution
from .serializer import deserialize, serialize


class RoutineEngine:
    def __init__(self, policy):
        self.policy = policy

        self._execution_context = threading.local()
        self._loop = None
        self._result_queue = queue.Queue()
        self._status = 'IDLE'
        self._task_queue = queue.Queue()

    @property
    def status(self):
        return self._status

    @property
    def result_queue(self):
        return self._result_queue

    def schedule_executable(self, run_id, executable, arguments):
        if isinstance(executable, TaskExecutable):
            self._schedule_task_executable(run_id, executable, arguments)
        else:
            self._schedule_workflow_executable(run_id, executable, arguments)

    def _schedule_workflow_executable(self, run_id, executable, arguments):
        execution = self.policy.create_scheduled_execution(run_id,
                                                           executable,
                                                           arguments)

        workflow_loop = asyncio.new_event_loop()
        thread = threading.Thread(target=self._run_workflow,
                                  args=(workflow_loop, execution, self._result_queue))
        thread.start()

    def _schedule_task_executable(self, run_id, executable, arguments):
        execution = self.policy.create_scheduled_execution(run_id,
                                                           executable,
                                                           arguments)
        self._task_queue.put(execution)

    @property
    def is_running(self):
        return self._loop is not None

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
        assert self._loop is not None

        self._loop.stop()
        self._loop.close()
        self._loop = None

        self.result_queue.put(dict(type='ENGINE_CLOSED'))

    async def _start(self):
        while True:
            execution = self._task_queue.get(block=True)
            self._status = 'WORKING'

            self._execution_context.parent_run_id = execution.run_id
            result = await execution()
            execution.cleanup()
            self._result_queue.put(dict(execution=execution,
                                        result=result,
                                        type='EXECUTION_COMPLETE'))
            self._status = 'IDLE'

            if self.policy.stop_engine_after_first_scheduled_executable_finishes:
                self.stop()

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
        execution = self.policy.create_subroutine_execution(parent_run_id,
                                                            executable,
                                                            arguments)

        result = await execution()

        execution.cleanup()
        return result
