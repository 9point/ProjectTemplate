from ...RoutineID import RoutineID


class TaskExecutable:
    def __init__(self, name, doc, version, run, is_coroutine, get_engine):
        self.e_type = 'Task'

        self.get_engine = get_engine
        self.is_coroutine = is_coroutine

        self.doc = doc
        self.name = name
        self.run = run
        self.version = version

    @property
    def routine_id(self):
        return RoutineID(rtype='tname',
                         project_name=None,
                         routine_name=self.name,
                         version=self.version)

    async def __call__(self, *args, **kwargs):
        engine = self.get_engine()
        assert(engine is not None)
        return await engine.run_executable(self, *args, **kwargs)
