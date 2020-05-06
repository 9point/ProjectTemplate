from utils.RoutineID import RoutineID


class TaskExecutable:
    def __init__(self, name, doc, version, run, is_coroutine):
        self.e_type = 'Task'

        self._engine = None
        self.is_coroutine = is_coroutine

        self.doc = doc
        self.name = name
        self.run = run
        self.version = version

    @property
    def routine_id(self):
        return RoutineID(project_name=None, routine_name=self.name, version=self.version)

    def set_engine(self, engine):
        self._engine = engine

    async def __call__(self, *args, **kwargs):
        assert(self._engine is not None)
        return await self._engine.exec_task(self, *args, **kwargs)
