import threading
import time

from static_codegen import mlservice_pb2, mlservice_pb2_grpc
from utils.models.WorkerDirective import WorkerDirective
from utils.models.WorkerDirectiveRequest import WorkerDirectiveRequest
from utils.worker_thread import Subscriber


class DirectiveStreamer:
    def __init__(self, channel, worker):
        super().__init__()

        self._channel = channel
        self._is_running = False
        self._listeners = []
        self._send_buffer = []
        self._worker = worker

    def start(self):
        assert(not self._is_running)

        self._is_running = True

        stub = self._create_stub()

        # NOTE: GRPC will run the generator on a separate thread. Even though
        # the generator is an infinite loop, it is not blocking. However, it
        # must handle grabbing state from a separate thread.
        responses = stub.RouteWorkerDirectives(_generator(self))

        # NOTE: The receiver intercepts GRPC messages. The receiver is
        # blocking and should be run on a separate thread.
        receiver_thread = threading.Thread(target=_receiver,
                                           args=(self, responses))

        # TODO: Need to be able to stop this thread. May need to keep a
        # reference to this thread somewhere. Not sure if it's a good idea to
        # keep an instance variable with the thread. Would that cause wierd
        # memory issues if the thread has access to itself?
        receiver_thread.start()

    def stop(self):
      # TODO: IMPLEMENT ME
        assert(False, 'Directive Streamer does not yet handle will_stop')

    def send(self, directive_request):
        assert(self._is_running)
        self._send_buffer.append(directive_request)

    def on(self, payload_key, cb):
        payload = {'payload_key': payload_key, 'cb': cb}
        self._listeners.append(payload)

        def stop():
            if payload not in self._listeners:
                return

            self._listeners.remove(payload)

        return stop

    def _create_stub(self):
        return mlservice_pb2_grpc.MLStub(self._channel)


def _receiver(instance, responses):
    for response in responses:
        directive = WorkerDirective.from_grpc_message(response)

        for listener in instance._listeners:
            if listener['payload_key'] == directive.payload_key:
                listener['cb'](directive)


def _generator(instance):
    assert(instance._is_running)

    yield WorkerDirectiveRequest(payload_key='v1.worker.ready',
                                 payload={},
                                 worker_id=instance._worker.id).to_grpc_message()

    loop_secs = 5

    while instance._is_running:
        if len(instance._send_buffer) > 0:
            # Copy into local variable then clear buffer. This is more
            # thread safe.
            send_buffer = instance._send_buffer[:]
            instance._send_buffer.clear()

            for request in send_buffer:
                yield request.to_grpc_message()

        time.sleep(loop_secs)
