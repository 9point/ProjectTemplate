import datetime
import json

from static_codegen import mlservice_pb2


class WorkerDirective:
    def __init__(self,
                 id,
                 created_at,
                 updated_at,
                 is_deleted,
                 directive_type,
                 from_worker_id,
                 payload_key,
                 payload,
                 to_worker_id):
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.directive_type = directive_type
        self.from_worker_id = from_worker_id
        self.is_deleted = is_deleted
        self.payload_key = payload_key
        self.payload = payload
        self.to_worker_id = to_worker_id

    @staticmethod
    def from_grpc_message(message):
        id = message.id
        created_at = datetime.datetime.fromtimestamp(message.created_at)
        updated_at = datetime.datetime.fromtimestamp(message.updated_at)
        is_deleted = message.is_deleted
        directive_type = message.directive_type
        from_worker_id = message.from_worker_id
        payload_key = message.payload_key
        payload = json.loads(message.payload)
        to_worker_id = message.to_worker_id

        return WorkerDirective(id=id,
                               created_at=created_at,
                               updated_at=updated_at,
                               is_deleted=is_deleted,
                               directive_type=directive_type,
                               from_worker_id=from_worker_id,
                               payload_key=payload_key,
                               payload=payload,
                               to_worker_id=to_worker_id)

    def to_grpc_message(self):
        id = self.id
        created_at = datetime.datetime.timestamp(self.created_at)
        updated_at = datetime.datetime.timestamp(self.updated_at)
        is_deleted = self.is_deleted
        directive_type = self.directive_type
        from_worker_id = self.from_worker_id
        payload_key = self.payload_key
        payload = json.dumps(self.payload)
        to_worker_id = self.to_worker_id

        return mlservice_pb2.Obj_WorkerDirective(id=id,
                                                 created_at=created_at,
                                                 updated_at=updated_at,
                                                 is_deleted=is_deleted,
                                                 directive_type=directive_type,
                                                 from_worker_id=from_worker_id,
                                                 payload_key=payload_key,
                                                 payload=payload,
                                                 to_worker_id=to_worker_id)
