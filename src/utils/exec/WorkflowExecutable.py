from utils.RoutineID import RoutineID


class WorkflowExecutable:
    """
    Represents the code that defines a Workflow. Executing this code within the
    right environment will generate an AST which can be used to define the
    workflow.
    """

    def __init__(self, name, run):
        self.e_type = 'Workflow'

        self.name = name
        self.run = run

    @property
    def routine_id(self):
        return RoutineID(project_name=None, routine_name=self.name, version=None)

    def __call__(self, *args, **kwargs):
        pass
