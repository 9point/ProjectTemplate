import datetime

from utils.RoutineID import RoutineID


class Worker:
    def __init__(self, id, created_at, updated_at, is_deleted, project_id, routines, status):
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at
        self.is_deleted = is_deleted
        self.project_id = project_id
        self.routines = routines
        self.status = status

    @staticmethod
    def from_grpc_message(message):
        id = message.id
        created_at = datetime.datetime.fromtimestamp(message.created_at)
        updated_at = datetime.datetime.fromtimestamp(message.updated_at)
        is_deleted = message.is_deleted
        project_id = message.project_id
        routines = [
            RoutineID.parse(str_id) for str_id in message.routines.split('|')]
        status = message.status

        return Worker(id=id,
                      created_at=created_at,
                      updated_at=updated_at,
                      is_deleted=is_deleted,
                      project_id=project_id,
                      routines=routines,
                      status=status)
