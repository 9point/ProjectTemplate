
class ExecutableRegistry:
    def __init__(self):
        self._task_execs = []
        self._workflow_execs = []

    @property
    def task_execs(self):
        return self._task_execs

    @property
    def workflow_execs(self):
        return self._workflow_execs

    def get_routine(self, routine_id):
        for executable in self._task_execs:
            if executable.routine_id.is_match(routine_id):
                return executable

        for executable in self._workflow_execs:
            if executable.routine_id.is_match(routine_id):
                return executable

        return None

    def add_task_exec(self, task_exec):
        self._task_execs.append(task_exec)

    def add_workflow_exec(self, wf_exec):
        self._workflow_execs.append(wf_exec)
