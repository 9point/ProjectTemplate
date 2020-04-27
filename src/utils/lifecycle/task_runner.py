import threading
import time

from utils import task_mgr

_LISTENERS = []
_RUNNING_TASK_NAME = None


def start(task_name):
    start_task_thread = threading.Thread(target=_start_worker,
                                         args=(task_name,))
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


def on_task_complete():
    global _LISTENERS
    _LISTENERS.append({'key': 'task_completed'})


def _start_worker(task_name):
    global _RUNNING_TASK_NAME

    assert(_RUNNING_TASK_NAME is None)

    _RUNNING_TASK_NAME = task_name

    work_thread = threading.Thread(target=task_mgr.run_task,
                                   args=(_RUNNING_TASK_NAME,))
    work_thread.start()
    work_thread.join()

    print('Worker has completed its work. Joining.')
    _RUNNING_TASK_NAME = None


def _start_eventloop():
    global _LISTENERS
    global _RUNNING_TASK_NAME

    loop_secs = 5

    assert(_RUNNING_TASK_NAME is not None)
    task_name = _RUNNING_TASK_NAME

    while _RUNNING_TASK_NAME is not None:
        time.sleep(loop_secs)

    for listener in _LISTENERS:
        if listener['key'] == 'task_completed':
            listener['cb'](task_name)
