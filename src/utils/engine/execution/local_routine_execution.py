from . import create_execution_id


class LocalRoutineExecution:
    def __init__(self, executable, *args, **kwargs):
        self.executable = executable
        self.arguments = dict(args=args, kwargs=kwargs)
        self.local_id = create_execution_id()

    @property
    def routine_id(self):
        return self.executable.routine_id

    async def __call__(self):
        args = self.arguments['args']
        kwargs = self.arguments['kwargs']

        if self.executable.is_coroutine:
            return await self.executable.run(*args, **kwargs)
        else:
            return self.executable.run(*args, **kwargs)
