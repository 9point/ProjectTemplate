import datetime


class Project:
    def __init__(self, id, created_at, updated_at, is_deleted, name):
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_deleted = is_deleted
        self.name = name

    @staticmethod
    def from_grpc_message(message):
        id = message.id
        created_at = datetime.datetime.fromtimestamp(message.created_at)
        updated_at = datetime.datetime.fromtimestamp(message.updated_at)
        is_deleted = message.is_deleted
        name = message.name

        return Project(id=id,
                       created_at=created_at,
                       updated_at=updated_at,
                       is_deleted=is_deleted,
                       name=name)
