class LocalRunEngine:
    def execute_task(self, task, *args, **kwargs):
        return task.run(*args, **kwargs)

    def execute_workflow(self, wf, *args, **kwargs):
        return wf.run(*args, **kwargs)
