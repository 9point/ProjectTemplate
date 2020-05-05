from utils import lifecycle
from utils.exec.TaskExecutable import TaskExecutable
from utils.exec.WorkflowExecutable import WorkflowExecutable


def workflow(name):

    def inner(func):
        wf_exec = WorkflowExecutable(name, func)
        lifecycle.register_workflow_exec(wf_exec)

        return wrap_workflow_exec(wf_exec)

    return inner


def task(name, version):

    def inner(func):
        task_exec = TaskExecutable(name, func.__doc__, version, func)
        lifecycle.register_task_exec(task_exec)

        return wrap_task_exec(task_exec)

    return inner


def wrap_task_exec(executable):
    async def coro(*args, **kwargs):
        executable.set_engine(lifecycle.engine())
        return executable(*args, **kwargs)

    return coro


def wrap_workflow_exec(executable):
    async def coro(*args, **kwargs):
        executable.set_engine(lifecycle.engine())
        return executable(*args, **kwargs)

    return coro
