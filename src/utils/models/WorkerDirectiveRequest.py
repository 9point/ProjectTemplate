import json

from static_codegen import mlservice_pb2


class WorkerDirectiveRequest:
    def __init__(self, payload_key, payload, worker_id):
        self.payload_key = payload_key
        self.payload = payload
        self.worker_id = worker_id

    def to_grpc_message(self):
        payload_key = self.payload_key
        payload = json.dumps(self.payload)
        worker_id = self.worker_id

        return mlservice_pb2.Req_RouteWorkerDirective(payload_key=payload_key,
                                                      payload=payload,
                                                      worker_id=worker_id)
