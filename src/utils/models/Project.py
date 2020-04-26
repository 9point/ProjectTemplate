import datetime


class Project:
    def __init__(self, id, created_at, updated_at, is_deleted, image_name, name):
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_deleted = is_deleted
        self.image_name = image_name
        self.name = name

    @staticmethod
    def from_grpc_message(message):
        id = message.id
        created_at = datetime.datetime.fromtimestamp(message.created_at)
        updated_at = datetime.datetime.fromtimestamp(message.updated_at)
        is_deleted = message.is_deleted
        image_name = message.image_name
        name = message.name

        return Project(id=id,
                       created_at=created_at,
                       updated_at=updated_at,
                       is_deleted=is_deleted,
                       image_name=image_name,
                       name=name)
