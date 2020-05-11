from . import create_execution_id


class LocalRoutineExecution:
    def __init__(self, executable):
        self.executable = executable
        self.local_id = create_execution_id()

    async def __call__(self, *args, **kwargs):
        print('calling execution')
        if self.executable.is_coroutine:
            print('calling as coroutine')
            return await self.executable.run(*args, **kwargs)
        else:
            print('not coroutine')
            return self.executable.run(*args, **kwargs)
