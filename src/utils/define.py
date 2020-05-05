from utils import lifecycle
from utils.exec.TaskExecutable import TaskExecutable
from utils.exec.WorkflowExecutable import WorkflowExecutable


def workflow(name):

    def inner(func):
        wf = WorkflowExecutable(name, func)
        lifecycle.register_workflow_executable(wf)

        return wrap_workflow_exec(wf)

    return inner


def task(name, version):

    def inner(func):
        task = TaskExecutable(name, func.__doc__, version, func)
        lifecycle.register_task_executable(task)

        return wrap_task_exec(task)

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
