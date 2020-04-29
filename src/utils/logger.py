import datetime

from utils import lifecycle

_ORDER = 0


def write(*args):
    global _ORDER

    workflow_run_id = lifecycle.workflow_run_id()

    # TODO: Handle the case that this is trying to log something when 
    # nothing is running.
    assert(workflow_run_id is not None)

    str = ' '.join(args)
    payload = {'i': ['describable'],
               'descriptor': str,
               'order': _ORDER,
               'workflowRunID': workflow_run_id}

    lifecycle.send_directive('v1.log', payload)

    print(*args)
    _ORDER += 1
