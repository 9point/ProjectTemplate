import json
import threading
import time

from static_codegen import mlservice_pb2, mlservice_pb2_grpc
from utils import task_mgr

_CHANNEL = None
_PROJECT_PROTO = None
_WORKER_PROTO = None

_DIRECTIVE_BUFFER = []
_IS_RUNNING = False
_TASK_DIRECTIVE = None
_WORK_BUFFER = []


def start_routing(channel, project_proto, worker_proto):
    global _CHANNEL
    global _IS_RUNNING
    global _PROJECT_PROTO
    global _WORKER_PROTO

    assert(not _IS_RUNNING)

    _CHANNEL = channel
    _PROJECT_PROTO = project_proto
    _WORKER_PROTO = worker_proto
    _IS_RUNNING = True

    streamer_thread = threading.Thread(target=_streamer)
    streamer_thread.start()

    worker_thread = threading.Thread(target=_worker)
    worker_thread.start()

    _send_directive(_create_directive(_WORKER_PROTO.id,
                                      payload_key='v1.worker.ready', payload=json.dumps({})))


def stop_routing():
    global _IS_RUNNING

    assert(_IS_RUNNING)
    _IS_RUNNING = False


def _send_directive(directive):
    global _DIRECTIVE_BUFFER
    _DIRECTIVE_BUFFER.append(directive)


def _receive_directive(directive):
    pass


def _streamer():
    print('Running streamer')
    global _CHANNEL

    stub = _create_stub(_CHANNEL)
    responses = stub.RouteWorkerDirectives(_streamer_generator())
    _streamer_receiver(responses)


def _streamer_generator():
    global _DIRECTIVE_BUFFER
    global _IS_RUNNING

    loop_secs = 5
    while _IS_RUNNING:
        print('streamer generator loop')
        if len(_DIRECTIVE_BUFFER) > 0:
            print('clearing buffer')
            # Copy into local variable then clear buffer.
            directive_buffer = _DIRECTIVE_BUFFER[:]
            _DIRECTIVE_BUFFER.clear()

            for directive in directive_buffer:
                yield directive

        time.sleep(loop_secs)

    print('quitting generator')


def _streamer_receiver(responses):
    print('starting receiver')
    global _WORK_BUFFER

    # TODO: How do I cancel this?
    for response in responses:
        print('recieved response')
        # TODO: Error handling.
        if response.payload_key == 'v1.task.run':
            _WORK_BUFFER.append(response)

        elif response.payload_key == 'v1.task.kill':
            _WORK_BUFFER.append(response)

        elif response.payload_key == 'v1.heartbeat.check_pulse':
            _streamer_heartbeat(response)

        else:
            print(f'Unrecognized directive: {response.payload_key}')

    print('done receiving responses')


def _streamer_heartbeat(response):
    global _WORKER_PROTO

    assert(response.payload_key == 'v1.heartbeat.check_pulse')

    # TODO: Error handling when parsing json.
    payload = json.loads(response.payload)

    assert('id' in payload)

    directive = _create_directive(
        _WORKER_PROTO.id, payload_key='v1.heartbeat.give_pulse', payload=json.dumps({'id': payload['id']}))

    _send_directive(directive)


def _worker():
    global _IS_RUNNING
    global _WORK_BUFFER

    task_thread = None
    worker_sleep_secs = 5

    while _IS_RUNNING:
        if len(_WORK_BUFFER) > 0:
            # Copy into local variable then clear buffer.
            work_buffer = _WORK_BUFFER[:]
            _WORK_BUFFER.clear()

            for directive in work_buffer:
                if directive.payload_key is 'v1.task.run':
                    # TODO: Kill any tasks already running.
                    assert(task_thread is None)
                    # TODO: JSON parsing error handling.
                    payload = json.loads(directive.payload)
                    assert('task_name' in payload)
                    task_thread = threading.Thread(
                        target=task_mgr.run_task, args=(payload['task_name'],))

                elif directive.payload_key is 'v1.task.kill':
                    print('Not yet implementing kill task')

                else:
                    print(
                        f'Unrecognized worker directive: {directive.payload_key}')

        time.sleep(worker_sleep_secs)


def _create_stub(channel):
    return mlservice_pb2_grpc.MLStub(channel)


def _create_directive(worker_id, payload_key, payload):
    return mlservice_pb2.Req_RouteWorkerDirective(payload=json.dumps(payload),
                                                  payload_key=payload_key,
                                                  worker_id=worker_id)
