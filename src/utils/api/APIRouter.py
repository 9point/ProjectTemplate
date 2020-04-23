import time

from static_codegen import mlservice_pb2, mlservice_pb2_grpc
from utils import task_mgr


class APIRouter:
    def __init__(self, channel, project_proto, worker_proto):
        self._channel = channel
        self._project_proto = project_proto
        self._worker_proto = worker_proto

    def start(self):
        print('Starting router')
        stub = self._create_stub()
        responses = stub.RouteWorkerDirectives(self.generate_directives())

        for response in responses:
            print('Recevied response', response.id)

    def generate_directives(self):
        for _ in range(100):
            time.sleep(2000)
            request = mlservice_pb2.Req_RouteWorkerDirective(payload='{}',
                                                             payload_key='test',
                                                             worker_id=self._worker_proto.id)
            yield request

    def _create_stub(self):
        return mlservice_pb2_grpc.MLStub(self._channel)
