import grpc
import os

from datetime import datetime
from static_codegen import mlservice_pb2, mlservice_pb2_grpc
from utils import task_mgr
from utils.lifecycle import task_runner
from utils.lifecycle.Connection import Connection
from utils.models.WorkerDirectiveRequest import WorkerDirectiveRequest


_PROJECT_NAME = os.environ.get('PROJECT_NAME')
_IMAGE_NAME = os.environ.get('IMAGE_NAME')
_API_ENDPOINT = os.environ.get('API_ENDPOINT')

_CONNECTION = None


def start():
    global _CONNECTION

    assert(_CONNECTION is None)
    _CONNECTION = Connection()
    _CONNECTION.start()


def stop():
    # TODO: IMPLEMENT ME
    pass


def register_project():
    global _CONNECTION

    assert(_CONNECTION is not None)
    _CONNECTION.register_project()


def register_worker():
    global _CONNECTION

    assert(_CONNECTION is not None)
    _CONNECTION.register_worker()

    _CONNECTION.on_directive('v1.task.request_start',
                             _on_request_task_start)

    _CONNECTION.on_directive('v1.heartbeat.check_pulse',
                             _on_heartbeat_check_pulse)

    task_runner.on_task_complete(_on_task_completed)


def run_workflow(workflow_name):
    global _CONNECTION

    assert(_CONNECTION is not None)
    return _CONNECTION.run_workflow(workflow_name)


def send_directive(payload_key, payload):
    global _CONNECTION

    assert(_CONNECTION is not None)
    _CONNECTION.send_directive(payload_key, payload)


def workflow_run_id():
    return task_runner.running_workflow_run_id()

def _on_request_task_start(directive):
    global _CONNECTION

    assert('taskName' in directive.payload)
    assert('workflowRunID' in directive.payload)

    task_name = directive.payload['taskName']
    workflow_run_id = directive.payload['workflowRunID']
    task_runner.start(task_name, workflow_run_id)
    
    print('Starting task:')
    print(f'Task Name: {task_name}')
    print(f'Workflow Run ID: {workflow_run_id}')

    # TODO: project_id and task_id in payload.
    payload = {'taskName': task_name}
    _CONNECTION.send_directive('v1.task.starting', payload)


def _on_heartbeat_check_pulse(directive):
    global _CONNECTION

    assert(_CONNECTION is not None)

    assert('id' in directive.payload)

    status = 'IDLE' if task_runner.running_task_name() is None else 'WORKING'
    print('Sending status:', status)

    payload = {'id': directive.payload['id'], 'status': status}

    _CONNECTION.send_directive('v1.heartbeat.give_pulse', payload)


def _on_task_completed(task_name, workflow_run_id):
    if _CONNECTION is None:
        return

    payload = {'taskName': task_name, 'workflowRunID': workflow_run_id}
    _CONNECTION.send_directive(
        payload_key='v1.task.completed', payload=payload)
