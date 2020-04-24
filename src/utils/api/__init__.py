import grpc
import os

from datetime import datetime
from static_codegen import mlservice_pb2, mlservice_pb2_grpc
from utils import task_mgr
from utils.api.APIRouter import start_routing

_PROJECT_NAME = os.environ.get('PROJECT_NAME')
_IMAGE_NAME = os.environ.get('IMAGE_NAME')
_API_ENDPOINT = os.environ.get('API_ENDPOINT')


class _API:
    def __init__(self):
        self._channel = None
        self._project_proto = None
        self._worker_proto = None

    @property
    def is_started(self):
        return self._channel is not None

    def start(self):
        assert(self._channel is None)
        self._channel = grpc.insecure_channel(_API_ENDPOINT)

    def register_project(self):
        assert(self.is_started)

        workflows = task_mgr.get_workflows()
        tasks = task_mgr.get_tasks()

        assert(len(workflows) > 0)
        assert(len(tasks) > 0)

        stub = self._create_stub()

        request_register_project = mlservice_pb2.Req_RegisterProject(image_name=_IMAGE_NAME,
                                                                     name=_PROJECT_NAME)

        project_proto = stub.RegisterProject(request_register_project)

        requests_register_workflows = [mlservice_pb2.Req_RegisterWorkflow(
            name=wf.name, project_ref_id=project_proto.id) for wf in workflows]

        stub.RegisterWorkflows(iter(requests_register_workflows))

        requests_register_tasks = [mlservice_pb2.Req_RegisterTask(
            name=t.name, project_ref_id=project_proto.id, version=t.version) for t in tasks]

        stub.RegisterTasks(iter(requests_register_tasks))

        self._project_proto = project_proto

    def register_worker(self):
        assert(self.is_started)

        stub = self._create_stub()

        # Get the project. Assuming it has already been registered.

        request_get_project = mlservice_pb2.Req_GetProject(name=_PROJECT_NAME)

        project_proto = stub.GetProject(request_get_project)

        # Register the worker with the api.

        request_register_worker = mlservice_pb2.Req_RegisterWorker(
            project_id=project_proto.id)

        worker_proto = stub.RegisterWorker(request_register_worker)

        # Start the router which communicates with the backend.

        start_routing(self._channel, project_proto, worker_proto)

    def run_workflow(self):
        pass

    def _create_stub(self):
        assert(self._channel is not None)
        return mlservice_pb2_grpc.MLStub(self._channel)


_API_INSTANCE = _API()


def start_api():
    if not _API_INSTANCE.is_started:
        _API_INSTANCE.start()
    return _API_INSTANCE
