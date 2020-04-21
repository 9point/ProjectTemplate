import grpc
import os

from static_codegen import mlservice_pb2, mlservice_pb2_grpc
from utils import task_mgr

_PROJECT_NAME = os.environ.get('PROJECT_NAME')
_IMAGE_NAME = os.environ.get('IMAGE_NAME')
_API_ENDPOINT = os.environ.get('API_ENDPOINT')


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
        workflow_names = '|'.join([wf.name for wf in workflows])

        stub = self._create_stub()
        request = mlservice_pb2.Req_RegisterWorkflows(names=workflow_names,
                                                      project_ref_id=self._project_id)
        stub.RegisterWorkflows(request)

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
