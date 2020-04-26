import time
import threading

from static_codegen import mlservice_pb2, mlservice_pb2_grpc
from utils.models.WorkerDirective import WorkerDirective
from utils.models.WorkerDirectiveRequest import WorkerDirectiveRequest

_CHANNEL = None
_IS_RUNNING = False
_LISTENERS = []
_SEND_BUFFER = []
_WORKER = None


def start(channel, worker):
    global _CHANNEL
    global _IS_RUNNING
    global _WORKER

    assert(not _IS_RUNNING)

    _CHANNEL = channel
    _IS_RUNNING = True
    _WORKER = worker

    streamer_thread = threading.Thread(target=_start_impl)
    streamer_thread.start()


def stop():
  # TODO: IMPLEMENT ME
  # TODO: Clean up listeners
    pass


def is_running():
    global _IS_RUNNING
    return _IS_RUNNING


def on(payload_key, cb):
    global _LISTENERS

    _LISTENERS.append({'payload_key': payload_key, 'cb': cb})


def send(request):
    global _IS_RUNNING
    global _SEND_BUFFER

    assert(_IS_RUNNING)

    _SEND_BUFFER.append(request)


def _start_impl():
    stub = _create_stub()
    responses = stub.RouteWorkerDirectives(_generator())
    _receiver(responses)


def _generator():
    global _SEND_BUFFER
    global _IS_RUNNING
    global _WORKER

    yield WorkerDirectiveRequest(payload_key='v1.worker.ready',
                                 payload={},
                                 worker_id=_WORKER.id).to_grpc_message()

    loop_secs = 2
    while _IS_RUNNING:
        if len(_SEND_BUFFER) > 0:
            # Copy into local variable then clear buffer.
            send_buffer = _SEND_BUFFER[:]
            _SEND_BUFFER.clear()

            for request in send_buffer:
                yield request.to_grpc_message()

        time.sleep(loop_secs)


def _receiver(responses):
    global _LISTENERS
    global _WORKER

    # TODO: How do I cancel this?
    for response in responses:
        directive = WorkerDirective.from_grpc_message(response)

        if directive.payload_key == 'v1.heartbeat.check_pulse':
            payload_key = 'v1.heartbeat.give_pulse'
            payload = {'id': directive.payload['id']}
            worker_id = _WORKER.id
            send(WorkerDirectiveRequest(payload_key=payload_key,
                                        payload=payload,
                                        worker_id=worker_id))

        else:
            for listener in _LISTENERS:
                if listener.payload_key == directive.payload_key:
                    listener.cb(directive)


def _create_stub():
    global _CHANNEL
    return mlservice_pb2_grpc.MLStub(_CHANNEL)
