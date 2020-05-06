from utils.RoutineID import RoutineID


class WorkflowExecutable:
    """
    Represents the code that defines a Workflow. Executing this code within the
    right environment will generate an AST which can be used to define the
    workflow.
    """

    def __init__(self, name, run, is_coroutine):
        self.e_type = 'Workflow'

        self._engine = None
        self.is_coroutine = is_coroutine

        self.name = name
        self.run = run

    @property
    def routine_id(self):
        return RoutineID(project_name=None, routine_name=self.name, version=None)

    def set_engine(self, engine):
        self._engine = engine

    async def __call__(self, *args, **kwargs):
        assert(self._engine is not None)
        return await self._engine.exec_workflow(self, *args, **kwargs)
