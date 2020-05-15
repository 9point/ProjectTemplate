import grpc
import os
import threading

from datetime import datetime
from static_codegen import mlservice_pb2, mlservice_pb2_grpc
from .Connection import Connection
from .ExecutableRegistry import ExecutableRegistry
from .Logger import Logger
from ..models.WorkerDirectiveRequest import WorkerDirectiveRequest
from ..engine.local_run_engine import LocalRunEngine
from ..engine.remote_dispatch_engine import RemoteDispatchEngine
from ..engine.serializer import deserialize, serialize
from ..RoutineID import RoutineID


_API_ENDPOINT = os.environ.get('API_ENDPOINT')
_IMAGE_NAME = os.environ.get('IMAGE_NAME')
_PROJECT_NAME = os.environ.get('PROJECT_NAME')

_CONNECTION = None
_DIRECTIVE_SUBSCRIPTIONS = []
_ENGINE = None
_EXECUTABLE_REGISTRY = ExecutableRegistry()
_LOGGER = None
_WORKER_SUBSCRIPTIONS = []


def is_service_logger_running():
    global _LOGGER
    return _LOGGER is not None


def start_local_routine(executable, *args, **kwargs):
    global _ENGINE

    assert _ENGINE is None

    _ENGINE = LocalRunEngine()
    return _ENGINE.start(executable, *args, **kwargs)


def start_remote_routine(executable, *args, **kwargs):
    global _CONNECTION
    assert _CONNECTION is not None

    arguments = dict(args=args, kwargs=kwargs)
    print('args', arguments)
    return _CONNECTION.run_routine(executable.routine_id, arguments)


def start_engine():
    """
    Starts the engine, which is in charge of running the all the routines.
    This method does not return unless there is a fatal erro with the engine.
    """

    global _CONNECTION
    global _ENGINE

    _ENGINE = RemoteDispatchEngine(_CONNECTION)
    engine_results_thread = threading.Thread(target=_engine_result_thread)
    engine_results_thread.start()

    _ENGINE.start()


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
    return _CONNECTION.register_project(_EXECUTABLE_REGISTRY)


def register_worker():
    global _CONNECTION
    global _DIRECTIVE_SUBSCRIPTIONS

    assert(_CONNECTION is not None)

    worker = _CONNECTION.register_worker(_EXECUTABLE_REGISTRY)

    _DIRECTIVE_SUBSCRIPTIONS.extend([
        _CONNECTION.on_directive('v1.routine.request_start',
                                 _on_routine_request_start),

        _CONNECTION.on_directive('v1.heartbeat.check_pulse',
                                 _on_heartbeat_check_pulse),
    ])

    return worker


def register_task_exec(task_exec):
    global _EXECUTABLE_REGISTRY
    _EXECUTABLE_REGISTRY.add_task_exec(task_exec)


def get_task_execs():
    global _EXECUTABLE_REGISTRY
    return _EXECUTABLE_REGISTRY.task_execs


def register_workflow_exec(wf_exec):
    global _EXECUTABLE_REGISTRY
    _EXECUTABLE_REGISTRY.add_workflow_exec(wf_exec)


def get_workflow_execs():
    global _EXECUTABLE_REGISTRY
    return _EXECUTABLE_REGISTRY.workflow_execs


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


def _engine_result_thread():
    global _ENGINE
    global _CONNECTION

    assert _CONNECTION is not None
    assert _ENGINE is not None

    while True:
        execution, result = _ENGINE.result_queue.get(block=True)
        print('Finished execution with result:', result)

        # TODO: To make this more robust, if a connection to the service
        # fails, should hold on to the result until the connection
        # is re-established.
        assert _CONNECTION is not None
        payload_key = 'v1.routine.completed'
        payload = dict(result=serialize(result),
                       routineID=str(execution.routine_id),
                       runID=execution.run_id)
        _CONNECTION.send_directive(payload_key, payload)


def _on_heartbeat_check_pulse(directive):
    global _CONNECTION
    global _ENGINE

    assert _CONNECTION is not None
    assert _ENGINE is not None

    assert 'id' in directive.payload

    status = _ENGINE.status
    print('Sending status:', status)

    payload = {'id': directive.payload['id'], 'status': status}

    _CONNECTION.send_directive('v1.heartbeat.give_pulse', payload)


def _on_routine_request_start(directive):
    print('received request start')

    global _CONNECTION
    global _ENGINE
    global _EXECUTABLE_REGISTRY

    assert _ENGINE is not None

    assert 'arguments' in directive.payload
    assert 'localRunID' in directive.payload
    assert 'routineID' in directive.payload
    assert 'runID' in directive.payload

    routine_id = RoutineID.parse(directive.payload['routineID'])
    run_id = directive.payload['runID']
    executable = _EXECUTABLE_REGISTRY.get_routine(routine_id)

    arguments = deserialize(directive.payload['arguments'])
    _ENGINE.schedule_executable(executable, run_id, arguments)


def _on_engine_terminated():
    global _ENGINE

    assert _ENGINE is not None

    # payload = {'taskName': task_name, 'workflowRunID': workflow_run_id}
    # _CONNECTION.send_directive(
    #     payload_key='v1.task.completed', payload=payload)
