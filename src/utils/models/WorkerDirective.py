import datetime
import json

from static_codegen import mlservice_pb2


class WorkerDirective:
    def __init__(self, id, created_at, updated_at, is_deleted, payload_key, payload, worker_id):
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_deleted = is_deleted
        self.payload_key = payload_key
        self.payload = payload
        self.worker_id = worker_id

    @staticmethod
    def from_grpc_message(message):
        id = message.id
        created_at = datetime.datetime.fromtimestamp(message.created_at)
        updated_at = datetime.datetime.fromtimestamp(message.updated_at)
        is_deleted = message.is_deleted
        payload_key = message.payload_key
        payload = json.loads(message.payload)
        worker_id = message.worker_id

        return WorkerDirective(id=id,
                               created_at=created_at,
                               updated_at=updated_at,
                               is_deleted=is_deleted,
                               payload_key=payload_key,
                               payload=payload,
                               worker_id=worker_id)

    def to_grpc_message(self):
        id = self.id
        created_at = datetime.datetime.timestamp(self.created_at)
        updated_at = datetime.datetime.timestamp(self.updated_at)
        is_deleted = self.is_deleted
        payload_key = self.payload_key
        payload = json.dumps(self.payload)
        worker_id = self.worker_id

        return mlservice_pb2.Obj_WorkerDirective(id=id,
                                                 created_at=created_at,
                                                 updated_at=updated_at,
                                                 is_deleted=is_deleted,
                                                 payload_key=payload_key,
                                                 payload=payload,
                                                 worker_id=worker_id)
