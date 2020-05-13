import os

from ...RoutineID import RoutineID

_PROJECT_NAME = os.environ.get('PROJECT_NAME')

assert(_PROJECT_NAME is not None)


class WorkflowExecutable:
    def __init__(self, name, run, is_coroutine, get_engine):
        self.e_type = 'Workflow'

        self.get_engine = get_engine
        self.is_coroutine = is_coroutine

        self.name = name
        self.run = run

    @property
    def routine_id(self):
        return RoutineID(rtype='wfname',
                         project_name=_PROJECT_NAME,
                         routine_name=self.name,
                         version=None)

    async def __call__(self, *args, **kwargs):
        engine = self.get_engine()
        assert(engine is not None)
        return await engine.run_executable(self, *args, **kwargs)
