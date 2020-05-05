import os

_PROJECT_NAME = os.environ.get('PROJECT_NAME')


class RoutineID:
    def __init__(self, project_name, routine_name, version):
        self.project_name = project_name
        self.routine_name = routine_name
        self.version = version

    @staticmethod
    def from_string(str_id):
        tokens = str_id.split(':')

        assert(len(tokens) in [1, 2, 3])

        if len(tokens) == 3:
            project_name = tokens[0]
            routine_name = tokens[1]
            version = tokens[2]

        if len(tokens) == 2:
            project_name = None
            routine_name = tokens[0]
            version = tokens[1]

        # TODO: Want to add support for database ids here. Would need
        # to disambiguate if this token is that of a db id or a routine name.
        if len(tokens) == 1:
            project_name = None
            routine_name = tokens[0]
            version = None

        return RoutineID(project_name, routine_name, version)

    def is_match(self, other):
        project1 = _PROJECT_NAME if self.project_name is None else self.project_name
        project2 = _PROJECT_NAME if other.project_name is None else other.project_name

        if project1 != project2:
            return False

        routine1 = self.routine_name
        routine2 = other.routine_name

        if routine1 != routine2:
            return False

        if any([v is None for v in [self.version, other.version]]):
            return True

        return self.version == other.version
