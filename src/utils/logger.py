import datetime
import threading

from utils import lifecycle


def write(*args):
    workflow_run_id = lifecycle.workflow_run_id()

    # TODO: Should let the logger setup the workflow run id.
    assert(workflow_run_id is not None)

    content = ' '.join(args)
    payload = {'content': content,
               'logType': 'messageSend',
               'workflowRunID': workflow_run_id}

    lifecycle.log(payload)

    print(*args)


def progressbar(key, name):
    return _ProgressBar(key, name)


class _ProgressBar:
    def __init__(self, key, name):
        self.key = key
        self.name = name

    def set_progress(self, decimal):
        if decimal < 0 or decimal > 1:
            raise InvalidProgressValue()

        workflow_run_id = lifecycle.workflow_run_id()

        # TODO: Should let the logger setup the workflow run id.
        assert(workflow_run_id is not None)

        payload = {'key': self.key,
                   'logType': 'progressBarSet',
                   'name': self.name,
                   'progress': decimal,
                   'workflowRunID': workflow_run_id}

        lifecycle.log(payload)

    def show(self):
        workflow_run_id = lifecycle.workflow_run_id()

        # TODO: Should let the logger setup the workflow run id.
        assert(workflow_run_id is not None)

        payload = {'key': self.key,
                   'logType': 'progressBarShow',
                   'name': self.name,
                   'workflowRunID': workflow_run_id}

        lifecycle.log(payload)


class InvalidProgressValue(Exception):
    pass
