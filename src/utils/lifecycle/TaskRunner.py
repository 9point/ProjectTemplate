import threading

from utils import task_mgr
from utils.worker_thread import Subscriber


class TaskRunner(Subscriber):
    def __init__(self):
        super().__init__()
        self._active_task_name = None
        self._active_workflow_run_id = None
        self._listeners = []
        self._pending_task_name = None
        self._pending_workflow_run_id = None
        self._task_thread = None

    @property
    def active_task_name(self):
        return self._active_task_name

    @property
    def active_workflow_run_id(self):
        return self._active_workflow_run_id

    def start_task(self, task_name, workflow_run_id):
        assert(self._active_task_name is None)
        assert(self._active_workflow_run_id is None)
        assert(self._pending_task_name is None)
        assert(self._pending_workflow_run_id is None)

        self._pending_workflow_run_id = workflow_run_id
        self._pending_task_name = task_name

    def on_task_complete(self, cb):
        self._listeners.append({'cb': cb, 'key': 'task_completed'})

    def did_start(self):
        pass

    def will_stop(self):
        # TODO: IMPLEMENT ME. Need to close out the running task, if
        # there is one.
        pass

    def minimum_loop_time_secs(self):
        if self._active_task_name is None:
            return 5

        return 60

    def loop(self):
        # If we have a pending task, we need to start that task.
        if self._pending_task_name is not None:
            assert(self._pending_workflow_run_id is not None)
            assert(self._active_task_name is None)
            assert(self._active_workflow_run_id is None)

            self._active_workflow_run_id = self._pending_workflow_run_id
            self._active_task_name = self._pending_task_name
            self._pending_workflow_run_id = None
            self._pending_task_name = None

            task_thread = threading.Thread(target=_start_task_thread,
                                           args=(self,))
            task_thread.start()


def _start_task_thread(instance):
    task_name = instance._active_task_name
    workflow_run_id = instance._active_workflow_run_id

    assert(task_name is not None)
    assert(workflow_run_id is not None)

    task_thread = threading.Thread(target=task_mgr.run_task,
                                   args=(task_name,))

    task_thread.start()
    task_thread.join()

    # NOTE: It is important to unset the workflow run id before the
    # task name. This is a safer approach when dealing with
    # multiple threads.
    instance._active_workflow_run_id = None
    instance._active_task_name = None

    for listener in instance._listeners:
        if listener['key'] == 'task_completed':
            listener['cb'](task_name, workflow_run_id)
