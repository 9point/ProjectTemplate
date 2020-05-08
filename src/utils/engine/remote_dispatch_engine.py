

class RemoteDipsatchEngine:
    def __init__(self, connection):
        self._connection = connection

    async def exec_task(self, task_exec, *args, **kwargs):
        pass

    async def exec_workflow(self, wf_exec, *args, **kwargs):
        pass
