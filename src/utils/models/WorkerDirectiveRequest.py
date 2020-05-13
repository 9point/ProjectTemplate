import json

from static_codegen import mlservice_pb2


class WorkerDirectiveRequest:
    def __init__(self, payload_key, payload, from_worker_id):
        self.payload_key = payload_key
        self.payload = payload
        self.from_worker_id = from_worker_id

    def to_grpc_message(self):
        payload_key = self.payload_key
        payload = json.dumps(self.payload)
        from_worker_id = self.from_worker_id

        return mlservice_pb2.Req_RouteWorkerDirective(payload_key=payload_key,
                                                      payload=payload,
                                                      from_worker_id=from_worker_id)
