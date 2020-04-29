import threading
import time

from utils import task_mgr

_LISTENERS = []
_RUNNING_TASK_NAME = None
_RUNNING_WORKFLOW_RUN_ID = None


def start(task_name, workflow_run_id):
    start_task_thread = threading.Thread(target=_start_worker,
                                         args=(task_name, workflow_run_id))
    start_task_thread.start()

    event_thread = threading.Thread(target=_start_eventloop)
    event_thread.start()


def stop():
    # TODO: IMPLEMENT ME
    global _RUNNING_TASK_NAME

    assert(_RUNNING_TASK_NAME is not None)


def running_task_name():
    global _RUNNING_TASK_NAME
    return _RUNNING_TASK_NAME


def running_workflow_run_id():
    global _RUNNING_WORKFLOW_RUN_ID
    return _RUNNING_WORKFLOW_RUN_ID


def on_task_complete(cb):
    global _LISTENERS
    _LISTENERS.append({'cb': cb, 'key': 'task_completed'})


def _start_worker(task_name, workflow_run_id):
    global _LISTENERS
    global _RUNNING_TASK_NAME
    global _RUNNING_WORKFLOW_RUN_ID

    assert(_RUNNING_TASK_NAME is None)
    assert(_RUNNING_WORKFLOW_RUN_ID is None)

    _RUNNING_TASK_NAME = task_name
    _RUNNING_WORKFLOW_RUN_ID = workflow_run_id

    work_thread = threading.Thread(target=task_mgr.run_task,
                                   args=(_RUNNING_TASK_NAME,))
    work_thread.start()
    work_thread.join()

    _RUNNING_WORKFLOW_RUN_ID = None
    _RUNNING_TASK_NAME = None

    # TODO: Need to check if thread is joining due to error. Need to report error.


def _start_eventloop():
    global _LISTENERS
    global _RUNNING_TASK_NAME
    global _RUNNING_WORKFLOW_RUN_ID

    loop_secs = 2

    # Need to wait for the task to get started.
    while _RUNNING_TASK_NAME is None:
        time.sleep(loop_secs)

    assert(_RUNNING_TASK_NAME is not None)
    assert(_RUNNING_WORKFLOW_RUN_ID is not None)

    task_name = _RUNNING_TASK_NAME
    workflow_id = _RUNNING_WORKFLOW_RUN_ID

    while _RUNNING_TASK_NAME is not None:
        time.sleep(loop_secs)

    for listener in _LISTENERS:
        if listener['key'] == 'task_completed':
            listener['cb'](task_name, workflow_id)
