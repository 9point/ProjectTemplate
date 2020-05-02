import grpc
import os
import time

from static_codegen import mlservice_pb2, mlservice_pb2_grpc
from utils import task_mgr
from utils.lifecycle.DirectiveStreamer import DirectiveStreamer
from utils.models.Project import Project
from utils.models.Worker import Worker
from utils.models.WorkerDirectiveRequest import WorkerDirectiveRequest

_API_ENDPOINT = os.environ.get('API_ENDPOINT')
_IMAGE_NAME = os.environ.get('IMAGE_NAME')
_PROJECT_NAME = os.environ.get('PROJECT_NAME')


# TODO: Rename to DirectiveConnection
class Connection:
    def __init__(self):
        self._channel = None
        self._directive_streamer = None
        self._project = None
        self._worker = None

    def start(self):
        assert(self._channel is None)
        self._channel = grpc.insecure_channel(_API_ENDPOINT)

    def stop(self):
        # TODO: IMPLEMENT ME!
        pass

    def register_project(self):
        """
        Register this project with the API Service. This gives the API
        Service any information about what this worker is capable of working
        on. Calling this method does not register the worker and will not make
        the worker available for accepting directives.
        """

        assert(self._channel is not None)

        workflows = task_mgr.get_workflows()
        tasks = task_mgr.get_tasks()

        assert(len(workflows) > 0)
        assert(len(tasks) > 0)

        stub = self._create_stub()

        request_register_project = mlservice_pb2.Req_RegisterProject(image_name=_IMAGE_NAME,
                                                                     name=_PROJECT_NAME)

        project_proto = stub.RegisterProject(request_register_project)

        requests_register_tasks = [
            mlservice_pb2.Req_RegisterTask(name=t.name,
                                           project_ref_id=project_proto.id,
                                           version=t.version)
            for t in tasks]

        tasks_proto = [
            t for t in stub.RegisterTasks(iter(requests_register_tasks))]

        requests_register_workflows = [
            mlservice_pb2.Req_RegisterWorkflow(name=wf.name,
                                               project_ref_id=project_proto.id,
                                               task_names='|'.join(wf.task_names))
            for wf in workflows]

        workflows_proto = [
            wf for wf in stub.RegisterWorkflows(iter(requests_register_workflows))]

        self._project = Project.from_grpc_message(project_proto)
        return self._project

    def register_worker(self):
        """
        Registers the worker with the API Service. This will let the API
        Service that this worker is ready and connected so it can receive
        directives from the service.

        Note that this method must assumes the project associated with this
        worker is already registered and up-to-date.
        """

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

        self._directive_streamer = DirectiveStreamer(self._channel,
                                                     self._worker)
        self._directive_streamer.start()

        return self._worker

    def run_workflow(self, workflow_name):
        assert(self._channel is not None)

        stub = self._create_stub()

        # Get the project. Assuming it has already been registered.

        request_get_project = mlservice_pb2.Req_GetProject(name=_PROJECT_NAME)
        project_proto = stub.GetProject(request_get_project)
        project = Project.from_grpc_message(project_proto)

        request = mlservice_pb2.Req_RunWorkflow(project_id=project.id,
                                                workflow_name=workflow_name)

        self._project = project

        return stub.RunWorkflow(request)

    def on_directive(self, payload_key, cb):
        self._directive_streamer.on(payload_key, cb)

    def send_directive(self, payload_key, payload):
        assert(self._worker is not None)
        assert(self._directive_streamer is not None)

        request = WorkerDirectiveRequest(payload_key=payload_key,
                                         payload=payload,
                                         worker_id=self._worker.id)

        self._directive_streamer.send(request)

    def _create_stub(self):
        assert(self._channel is not None)
        return mlservice_pb2_grpc.MLStub(self._channel)
