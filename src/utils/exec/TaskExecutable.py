from utils.RoutineID import RoutineID


class TaskExecutable:
    """
    Represents the code that executes a task. Running the code will cause the
    task to start running.
    """

    def __init__(self, name, doc, version, run):
        self.e_type = 'Task'

        self.doc = doc
        self.name = name
        self.run = run
        self.version = version

    @property
    def routine_id(self):
        return RoutineID(project_name=None, routine_name=self.name, version=self.version)

    def __call__(self, *args, **kwargs):
        pass
