import os

_PROJECT_NAME = os.environ.get('PROJECT_NAME')


class RoutineID:
    def __init__(self,
                 rtype,
                 dbid=None,
                 project_name=None,
                 routine_name=None,
                 version=None):
        self.rtype = rtype
        self.dbid = dbid
        self.project_name = project_name
        self.routine_name = routine_name
        self.version = version

    @staticmethod
    def parse(str_id):
        tokens = str_id.split(':')

        rtype = tokens[0]
        assert(rtype in ['tdb', 'wfdb', 'tname', 'wfname'])

        if rtype == 'tdb' or rtype == 'wfdb':
            assert(len(tokens) == 2)
            return RoutineID(rtype=rtype, dbid=tokens[1])

        assert(len(tokens) in [2, 3, 4])

        if len(tokens) == 4:
            if rtype == 'wfname':
                raise InvalidRoutineID()

            project_name = tokens[1]
            routine_name = tokens[2]
            version = tokens[3]

        if len(tokens) == 3 and rtype == 'tname':
            project_name = None
            routine_name = tokens[1]
            version = tokens[2]

        elif len(tokens) == 3 and rtype == 'wfname':
            project_name = tokens[1]
            routine_name = tokens[2]
            version = None

        if len(tokens) == 2:
            project_name = None
            routine_name = tokens[1]
            version = None

        return RoutineID(rtype=rtype,
                         project_name=project_name,
                         routine_name=routine_name,
                         version=version)

    def is_match(self, other):
        if self.rtype != other.rtype:
            return False

        if self.rtype == 'tdb' or self.rtype == 'wfdb':
            return self.dbid == other.dbid

        if (
                self.project_name is not None
                and other.project_name is not None
                and self.project_name != other.project_name
        ):
            return False

        if self.routine_name != other.routine_name:
            return False

        return (
            self.version is None
            or other.version is None
            or self.version == other.version
        )

    def __str__(self):
        if self.rtype == 'tdb' or self.rtype == 'wfdb':
            return f'{self.rtype}:{self.dbid}'

        str_id = self.rtype

        if self.project_name is not None:
            str_id += f':{self.project_name}'

        str_id += f':{self.routine_name}'

        if self.version is not None:
            str_id += f':{self.version}'

        return str_id


class InvalidRoutineID(Exception):
    pass
