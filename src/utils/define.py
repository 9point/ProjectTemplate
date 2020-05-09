import inspect

from utils import lifecycle
from .engine.executable.task_executable import TaskExecutable
from .engine.executable.workflow_executable import WorkflowExecutable


def workflow(name):

    def inner(func):
        is_coroutine = inspect.iscoroutinefunction(func)

        wf_exec = WorkflowExecutable(name, func, is_coroutine, get_engine)
        lifecycle.register_workflow_exec(wf_exec)

        return wf_exec

    return inner


def task(name, version):

    def inner(func):
        is_coroutine = inspect.iscoroutinefunction(func)

        task_exec = TaskExecutable(name,
                                   func.__doc__,
                                   version,
                                   func,
                                   is_coroutine,
                                   get_engine)

        lifecycle.register_task_exec(task_exec)

        return task_exec

    return inner


# Don't want the executable objects talking directly to the lifecycle. But
# the lifecycle owns the engine and the engine will not yet be created when
# the executable objects are instantiated. To get around this, creating this
# abstract here. This method can be called by executable objects to get access
# to the engine.
def get_engine():
    return lifecycle.engine()
