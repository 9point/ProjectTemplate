
_TASK_MAP = {}


def register_tasks(tasks):
    pass


def run_task(name):
    print(name, _TASK_MAP)
    if name not in _TASK_MAP:
        raise InvalidTaskName()
    _TASK_MAP[name]['func']()


def define_task(version):
    print('Defining task!')
    def inner(func):
        task_config = {
            'doc': func.__doc__,
            'func': func,
            'task_name': func.__name__,
            'version': version
        }
        print('Defining task inner')
        print(task_config)
        _TASK_MAP[func.__name__] = task_config
        return func

    return inner


class InvalidTaskName(Exception):
    pass
