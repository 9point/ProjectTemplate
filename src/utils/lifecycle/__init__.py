import grpc
import os

from datetime import datetime
from static_codegen import mlservice_pb2, mlservice_pb2_grpc
from utils import task_mgr, worker_thread
from utils.lifecycle.Connection import Connection
from utils.lifecycle.Logger import Logger
from utils.lifecycle.TaskRunner import TaskRunner
from utils.models.WorkerDirectiveRequest import WorkerDirectiveRequest


_API_ENDPOINT = os.environ.get('API_ENDPOINT')
_IMAGE_NAME = os.environ.get('IMAGE_NAME')
_PROJECT_NAME = os.environ.get('PROJECT_NAME')

_CONNECTION = None
_ENGINE = None
_LOGGER = None
_TASK_RUNNER = None
_WORKER_SUBSCRIPTIONS = []


def start_worker():
    global _CONNECTION
    global _LOGGER
    global _TASK_RUNNER
    global _WORKER_SUBSCRIPTIONS

    assert(_CONNECTION is not None)
    assert(_TASK_RUNNER is None)

    worker_thread.start_thread()

    _TASK_RUNNER = TaskRunner()
    _LOGGER = Logger()

    _LOGGER.set_connection(_CONNECTION)

    _WORKER_SUBSCRIPTIONS.extend([
        worker_thread.add_subscriber(_TASK_RUNNER),
        worker_thread.add_subscriber(_LOGGER),
    ])


def stop_worker():
    # TODO: IMPLEMENT ME!
    pass


def start_connection():
    global _CONNECTION

    assert(_CONNECTION is None)

    # NOTE: The connection exists on a thread separate from the worker thread.
    _CONNECTION = Connection()
    _CONNECTION.start()


def stop_connection():
    # TODO: IMPLEMENT ME
    pass


def register_project():
    global _CONNECTION

    assert(_CONNECTION is not None)
    return _CONNECTION.register_project()


def register_worker():
    global _CONNECTION
    global _TASK_RUNNER

    assert(_CONNECTION is not None)

    worker = _CONNECTION.register_worker()

    _CONNECTION.on_directive('v1.task.request_start',
                             _on_request_task_start)

    _CONNECTION.on_directive('v1.heartbeat.check_pulse',
                             _on_heartbeat_check_pulse)

    _TASK_RUNNER.on_task_complete(_on_task_completed)

    return worker


def register_task_executable(task_exec):
    pass


def register_workflow_executable(wf_exec):
    pass


def run_workflow(workflow_name):
    global _CONNECTION

    assert(_CONNECTION is not None)
    return _CONNECTION.run_workflow(workflow_name)


def send_directive(payload_key, payload):
    global _CONNECTION

    assert(_CONNECTION is not None)
    _CONNECTION.send_directive(payload_key, payload)


def engine():
    global _ENGINE
    return _ENGINE


def log(payload):
    assert(_LOGGER is not None)
    _LOGGER.send_log(payload)


def workflow_run_id():
    global _TASK_RUNNER

    if _TASK_RUNNER is None:
        return None

    return _TASK_RUNNER.active_workflow_run_id


def _on_request_task_start(directive):
    global _CONNECTION
    global _TASK_RUNNER

    assert(_CONNECTION is not None)
    assert(_TASK_RUNNER is not None)

    assert('taskName' in directive.payload)
    assert('workflowRunID' in directive.payload)

    task_name = directive.payload['taskName']
    workflow_run_id = directive.payload['workflowRunID']
    _TASK_RUNNER.start_task(task_name, workflow_run_id)

    print('Starting task:')
    print(f'Task Name: {task_name}')
    print(f'Workflow Run ID: {workflow_run_id}')

    # TODO: project_id and task_id in payload.
    payload = {'taskName': task_name}
    _CONNECTION.send_directive('v1.task.starting', payload)


def _on_heartbeat_check_pulse(directive):
    global _CONNECTION
    global _TASK_RUNNER

    assert(_CONNECTION is not None)
    assert(_TASK_RUNNER is not None)

    assert('id' in directive.payload)

    status = 'IDLE' if _TASK_RUNNER.active_task_name is None else 'WORKING'
    print('Sending status:', status)

    payload = {'id': directive.payload['id'], 'status': status}

    _CONNECTION.send_directive('v1.heartbeat.give_pulse', payload)


def _on_task_completed(task_name, workflow_run_id):
    if _CONNECTION is None:
        return

    payload = {'taskName': task_name, 'workflowRunID': workflow_run_id}
    _CONNECTION.send_directive(
        payload_key='v1.task.completed', payload=payload)
