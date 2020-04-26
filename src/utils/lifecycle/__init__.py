import grpc
import os

from datetime import datetime
from static_codegen import mlservice_pb2, mlservice_pb2_grpc
from utils import task_mgr
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

    _CONNECTION.on_directive('v1.task.request_run',
                             _on_request_task_run)

    _CONNECTION.on_directive('v1.heartbeat.check_pulse',
                             _on_heartbeat_check_pulse)


def _on_request_task_run(directive):
    print('on request task run', directive.payload)


def _on_heartbeat_check_pulse(directive):
    global _CONNECTION

    assert(_CONNECTION is not None)

    print('checking pulse')

    assert('id' in directive.payload)

    payload = {'id': directive.payload['id'], 'status': 'IDLE'}

    _CONNECTION.send_directive('v1.heartbeat.give_pulse', payload)
