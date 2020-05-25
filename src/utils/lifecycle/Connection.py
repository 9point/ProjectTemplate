import grpc
import json
import os
import time

from static_codegen import mlservice_pb2, mlservice_pb2_grpc
from utils.lifecycle.DirectiveStreamer import DirectiveStreamer
from utils.models.Project import Project
from utils.models.Worker import Worker
from utils.models.WorkerDirectiveRequest import WorkerDirectiveRequest
from utils.RoutineID import RoutineID
from ..engine.execution import create_local_run_id
from ..engine.serializer import serialize

_API_ENDPOINT = os.environ.get('API_ENDPOINT')
_IMAGE_NAME = os.environ.get('IMAGE_NAME')
_PROJECT_NAME = os.environ.get('PROJECT_NAME')


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

    def register_project(self, executable_registry):
        """
        Register this project with the API Service. This gives the API
        Service any information about what this worker is capable of working
        on. Calling this method does not register the worker and will not make
        the worker available for accepting directives.
        """

        assert(self._channel is not None)

        workflow_execs = executable_registry.workflow_execs
        task_execs = executable_registry.task_execs

        assert(len(workflow_execs) > 0)
        assert(len(task_execs) > 0)

        stub = self._create_stub()

        request_register_project = mlservice_pb2.Req_RegisterProject(
            name=_PROJECT_NAME)

        project_proto = stub.RegisterProject(request_register_project)

        requests_register_tasks = [
            mlservice_pb2.Req_RegisterTask(name=t.name,
                                           project_ref_id=project_proto.id,
                                           version=t.version)
            for t in task_execs]

        tasks_proto = [
            t for t in stub.RegisterTasks(iter(requests_register_tasks))]

        task_ids = '|'.join([proto.id for proto in tasks_proto])

        requests_register_workflows = [
            mlservice_pb2.Req_RegisterWorkflow(name=wf.name,
                                               project_ref_id=project_proto.id)
            for wf in workflow_execs]

        workflows_proto = [
            wf for wf in stub.RegisterWorkflows(iter(requests_register_workflows))]

        workflow_ids = '|'.join([proto.id for proto in workflows_proto])

        request_register_container_image = mlservice_pb2.Req_RegisterContainerImage(name=_IMAGE_NAME,
                                                                                    project_id=project_proto.id,
                                                                                    protocol='v1.python',
                                                                                    task_ids=task_ids,
                                                                                    workflow_ids=workflow_ids)

        container_image_proto = stub.RegisterContainerImage(
            request_register_container_image)

        self._project = Project.from_grpc_message(project_proto)
        return self._project

    def register_worker(self, executable_registry, accepts_work_requests):
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

        execs = executable_registry.task_execs + executable_registry.workflow_execs
        str_ids = [str(e.routine_id) for e in execs]
        routines_str = '|'.join(str_ids)

        request_register_worker = mlservice_pb2.Req_RegisterWorker(
            accepts_work_requests=accepts_work_requests,
            project_id=project_proto.id,
            routines=routines_str)

        worker_proto = stub.RegisterWorker(request_register_worker)

        self._project = Project.from_grpc_message(project_proto)
        self._worker = Worker.from_grpc_message(worker_proto)

        self._directive_streamer = DirectiveStreamer(self._channel,
                                                     self._worker)
        self._directive_streamer.start()

        return self._worker

    def run_routine(self, routine_id, arguments):
        assert(self._channel is not None)
        stub = self._create_stub()
        serial_arguments = serialize(arguments)
        run_routine = mlservice_pb2.Req_RunRoutine(routine_id=str(routine_id),
                                                   local_run_id=create_local_run_id(),
                                                   arguments=json.dumps(serial_arguments))

        return stub.RunRoutine(run_routine)

    def on_directive(self, payload_key, cb):
        return self._directive_streamer.on(payload_key, cb)

    def send_directive(self, payload_key, payload):
        assert self._worker is not None
        assert self._directive_streamer is not None

        request = WorkerDirectiveRequest(payload_key=payload_key,
                                         payload=payload,
                                         from_worker_id=self._worker.id)

        self._directive_streamer.send(request)

    def _create_stub(self):
        assert(self._channel is not None)
        return mlservice_pb2_grpc.MLStub(self._channel)
