import datetime

from utils import lifecycle

_LOG_PAYLOAD_KEY = 'v1.log'
_ORDER = 0


def write(*args):
    writer = _Writer()
    writer.write(*args)
    writer.send_and_clear_buffer()


class write_batch:
    def __init__(self):
        self.writer = None

    def __enter__(self):
        self.writer = _Writer()

    def __exit__(self, exc_type, exc_value, traceback):
        if self.writer is None:
            return

        # TODO: Proper error handling here.
        self.writer.send_and_clear_buffer()
        self.writer = None


def progressbar(key, name):
    return _ProgressBar(key, name)


# TODO: This does not handle multi-threaded calls. May need to tweak
# this in the future.
class _Writer:
    def __init__(self):
        self.workflow_run_id = lifecycle.workflow_run_id()
        self.buffer = []

    def write(self, *args):
        self.buffer.append(args)

    def send_and_clear_buffer(self, *args):
        global _LOG_PAYLOAD_KEY
        global _ORDER

        str = ''

        for i, args in enumerate(self.buffer):
            if i > 0:
                str += '\n'
            str += ' '.join(args)

        payload = {'i': ['describable'],
                   'descriptor': str,
                   'order': _ORDER,
                   'workflowRunID': self.workflow_run_id}

        print(str)

        lifecycle.send_directive(_LOG_PAYLOAD_KEY, payload)
        _ORDER += 1

        self.buffer.clear()


class _ProgressBar:
    def __init__(self, key, name):
        self.key = key
        self.name = name

    def set_progress(self, decimal):
        global _LOG_PAYLOAD_KEY
        global _ORDER

        if decimal < 0 or decimal > 1:
            raise InvalidProgressValue()

        workflow_run_id = lifecycle.workflow_run_id()

        # TODO: Handle the case that this is trying to log something when
        # nothing is running.
        assert(workflow_run_id is not None)

        payload = {'command': 'setProgress',
                   'i': ['progressbar'],
                   'key': self.key,
                   'name': self.name,
                   'order': _ORDER,
                   'progress': decimal,
                   'workflowRunID': workflow_run_id}

        lifecycle.send_directive(_LOG_PAYLOAD_KEY, payload)

    def show(self):
        global _LOG_PAYLOAD_KEY
        global _ORDER

        workflow_run_id = lifecycle.workflow_run_id()

        # TODO: Handle the case that this is trying to log something when
        # nothing is running.
        assert(workflow_run_id is not None)

        payload = {'command': 'show',
                   'i': ['progressbar'],
                   'key': self.key,
                   'name': self.name,
                   'order': _ORDER,
                   'workflowRunID': workflow_run_id}

        lifecycle.send_directive(_LOG_PAYLOAD_KEY, payload)

        _ORDER += 1


class InvalidProgressValue(Exception):
    pass
