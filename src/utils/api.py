import grpc
import os

from datetime import datetime
from static_codegen import mlservice_pb2, mlservice_pb2_grpc
from utils import task_mgr
from utils.storage import s3_append, s3_exists, s3_write

_PROJECT_NAME = os.environ.get('PROJECT_NAME')
_IMAGE_NAME = os.environ.get('IMAGE_NAME')
_API_ENDPOINT = os.environ.get('API_ENDPOINT')
_RUN_ID = os.environ.get('RUN_ID')


class _API:
    def __init__(self):
        self._channel = None
        self._project_id = None

    @property
    def is_started(self):
        return self._channel is not None

    def start(self):
        assert(self._channel is None)
        self._channel = grpc.insecure_channel(_API_ENDPOINT)

    def register_project(self):
        stub = self._create_stub()
        request = mlservice_pb2.Req_RegisterProject(image_name=_IMAGE_NAME,
                                                    name=_PROJECT_NAME)

        project = stub.RegisterProject(request)
        self._project_id = project.id

    def register_workflows(self):
        assert(self._project_id is not None)
        workflows = task_mgr.get_workflows()

        stub = self._create_stub()
        requests = [mlservice_pb2.Req_RegisterWorkflow(
            name=wf.name, project_ref_id=self._project_id) for wf in workflows]

        stub.RegisterWorkflows(iter(requests))

    def register_tasks(self):
        assert(self._project_id is not None)
        tasks = task_mgr.get_tasks()

        stub = self._create_stub()
        requests = [mlservice_pb2.Req_RegisterTask(
            name=t.name, project_ref_id=self._project_id, version=t.version) for t in tasks]

        stub.RegisterTasks(iter(requests))

    def _create_stub(self):
        assert(self._channel is not None)
        return mlservice_pb2_grpc.MLStub(self._channel)


_API_INSTANCE = _API()


class start_api():
    def __enter__(self):
        if not _API_INSTANCE.is_started:
            _API_INSTANCE.start()
        return _API_INSTANCE

    def __exit__(self, exc_type, exc_value, traceback):
        pass


def register_run_TMP():
    path = f'tmp/jobs/{_RUN_ID}.txt'

    if s3_exists(path):
        with s3_append(path) as file:
            now = datetime.now()
            file.write(f'[{now}]: Trying to create second job run.\n')
        print(f'Run with id {_RUN_ID} already exists.')
        return False

    with s3_write(path) as file:
        now = datetime.now()
        file.write(f'[{now}]: Starting run...\n')

    return True
