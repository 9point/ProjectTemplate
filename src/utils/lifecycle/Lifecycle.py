import grpc
import os

from datetime import datetime
from static_codegen import mlservice_pb2, mlservice_pb2_grpc
from utils import task_mgr
from utils.lifecycle.Connection import Connection


_PROJECT_NAME = os.environ.get('PROJECT_NAME')
_IMAGE_NAME = os.environ.get('IMAGE_NAME')
_API_ENDPOINT = os.environ.get('API_ENDPOINT')


class Lifecycle:
    def __init__(self):
        self._connection = None

    def start(self):
        assert(self._connection is None)
        self._connection = Connection()
        self._connection.start()

    def stop(self):
        # TODO: IMPLEMENT ME
        pass

    def register_project(self):
        assert(self._connection is not None)
        self._connection.register_project()

    def register_worker(self):
        assert(self._connection is not None)
        self._connection.register_worker()

        self._connection.on_directive('v1.task.request_run',
                                      self._on_request_task_run)

    def _on_request_task_run(self, directive):
        # NOTE: This may be running on a different thread.
        # Cannot rely on local variables.
        print('on request task run', directive.payload)
