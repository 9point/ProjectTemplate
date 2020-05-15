from . import create_local_run_id


class LocalRoutineExecution:
    def __init__(self, executable, run_id, arguments):
        self.executable = executable
        self.local_id = create_local_run_id()
        self.run_id = run_id
        self.arguments = arguments

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


    def cleanup(self):
        pass