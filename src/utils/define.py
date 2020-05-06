import inspect

from utils import lifecycle
from utils.exec.TaskExecutable import TaskExecutable
from utils.exec.WorkflowExecutable import WorkflowExecutable


def workflow(name):

    def inner(func):
        is_coroutine = inspect.iscoroutinefunction(func)

        wf_exec = WorkflowExecutable(name, func, is_coroutine)
        lifecycle.register_workflow_exec(wf_exec)

        return wrap_workflow_exec(wf_exec)

    return inner


def task(name, version):

    def inner(func):
        is_coroutine = inspect.iscoroutinefunction(func)

        task_exec = TaskExecutable(
            name, func.__doc__, version, func, is_coroutine)
        lifecycle.register_task_exec(task_exec)

        return wrap_task_exec(task_exec)

    return inner


def wrap_task_exec(executable):
    async def coro(*args, **kwargs):
        engine = lifecycle.engine()
        assert(engine is not None)
        executable.set_engine(engine)
        return await executable(*args, **kwargs)

    return coro


def wrap_workflow_exec(executable):
    async def coro(*args, **kwargs):
        engine = lifecycle.engine()
        assert(engine is not None)
        executable.set_engine(engine)
        return await executable(*args, **kwargs)

    return coro
