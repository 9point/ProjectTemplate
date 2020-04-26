import grpc
import os

from static_codegen import mlservice_pb2, mlservice_pb2_grpc
from utils import task_mgr
from utils.lifecycle import directive_streamer
from utils.models.Project import Project
from utils.models.Worker import Worker
from utils.models.WorkerDirectiveRequest import WorkerDirectiveRequest

_API_ENDPOINT = os.environ.get('API_ENDPOINT')
_IMAGE_NAME = os.environ.get('IMAGE_NAME')
_PROJECT_NAME = os.environ.get('PROJECT_NAME')


class Connection:
    def __init__(self):
        self._channel = None
        self._project = None
        self._worker = None

    def start(self):
        assert(self._channel is None)
        self._channel = grpc.insecure_channel(_API_ENDPOINT)

    def stop(self):
        # TODO: IMPLEMENT ME!
        pass

    def register_project(self):
        assert(self._channel is not None)

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

        self._project = Project.from_grpc_message(project_proto)

    def register_worker(self):
        assert(self._channel is not None)

        stub = self._create_stub()

        # Get the project. Assuming it has already been registered.

        request_get_project = mlservice_pb2.Req_GetProject(name=_PROJECT_NAME)

        project_proto = stub.GetProject(request_get_project)

        # Register the worker with the api.

        request_register_worker = mlservice_pb2.Req_RegisterWorker(
            project_id=project_proto.id)

        worker_proto = stub.RegisterWorker(request_register_worker)

        self._project = Project.from_grpc_message(project_proto)
        self._worker = Worker.from_grpc_message(worker_proto)
        self._start_directive_connection()

    def on_directive(self, payload_key, cb):
        directive_streamer.on(payload_key, cb)

    def _start_directive_connection(self):
        assert(self._channel is not None)
        assert(self._worker is not None)

        directive_streamer.start(self._channel, self._worker)

    def send_directive(self, payload_key, payload):
        assert(self._worker is not None)

        request = WorkerDirectiveRequest(payload_key=payload_key,
                                         payload=payload,
                                         worker_id=self._worker.id)

        directive_streamer.send(request)

    def _create_stub(self):
        assert(self._channel is not None)
        return mlservice_pb2_grpc.MLStub(self._channel)
