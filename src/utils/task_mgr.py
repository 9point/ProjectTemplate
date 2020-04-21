
_WORKFLOW_MAP = {}
_TASK_MAP = {}
_TASK_CALL_TRACKER = []


def register_workflows(workflows):
    pass


def run_workflow(name):
    if name not in _WORKFLOW_MAP:
        raise InvalidWorkflowName()

    workflow = _WORKFLOW_MAP[name]
    workflow()


def define_workflow(name):

    def inner(func):
        # TODO: Think about multi-threading here.
        assert(len(_TASK_CALL_TRACKER) == 0)

        func()  # Mutates call tracker under the hood.
        call_graph = _TASK_CALL_TRACKER[:]
        _TASK_CALL_TRACKER.clear()

        workflow = Workflow(name, call_graph)
        _WORKFLOW_MAP[name] = workflow

        return func

    return inner


def define_task(name, version):

    def inner(func):
        task = Task(func, name, version, func.__doc__)
        _TASK_MAP[name] = task

        def track_call():
            _TASK_CALL_TRACKER.append(name)

        return track_call

    return inner


def get_workflows():
    return list(_WORKFLOW_MAP.values())


def get_tasks():
    return list(_TASK_MAP.values())


class Workflow:
    def __init__(self, name, call_graph):
        self.name = name
        self.call_graph = call_graph

    def __call__(self):
        # TODO: For now, assuming a workflow is just a single task.
        assert(len(self.call_graph) == 1)
        task = _TASK_MAP[self.call_graph[0]]
        return task()


class Task:
    def __init__(self, run, name, version, doc):
        self.name = name
        self.version = version
        self.doc = doc
        self.run = run

    def __call__(self):
        return self.run()


class InvalidWorkflowName(Exception):
    pass


class InvalidTaskName(Exception):
    pass
