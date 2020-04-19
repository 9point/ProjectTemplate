import argparse
import grpc
import os

from bow_classifier import train as train_bow_classifier
from static_codegen import mlservice_pb2, mlservice_pb2_grpc
from utils.task_mgr import InvalidWorkflowName, register_workflows, run_workflow

_PROJECT_NAME = os.environ.get('PROJECT_NAME')
_IMAGE_NAME = os.environ.get('IMAGE_NAME')
_API_ENDPOINT = os.environ.get('API_ENDPOINT')


def run(commands):
    if len(commands) == 0:
        print('Error: Must provide task name to run.')
        exit(1)

    workflow_name = commands[0]
    print(f'Running command: "{workflow_name}"...')

    try:
        run_workflow(workflow_name)
    except InvalidWorkflowName:
        print(f'Error: Invalid workflow name: "{workflow_name}"')
        exit(1)


def register(commands):
    print('Registering Project...')


if __name__ == '__main__':
    register_workflows([train_bow_classifier])

    parser = argparse.ArgumentParser(description='Project Runner')
    parser.add_argument('commands', type=str, nargs='+')

    args = parser.parse_args()
    commands = args.commands

    if len(commands) == 0:
        print('error: No commands provided.')
        exit(1)

    # Make GRPC Connection.
    print(f'Registering project: {_PROJECT_NAME}')
    channel = grpc.insecure_channel(_API_ENDPOINT)
    stub = mlservice_pb2_grpc.MLStub(channel)
    request = mlservice_pb2.Req_RegisterProject(image_name=_IMAGE_NAME,
                                                name=_PROJECT_NAME)

    project = stub.RegisterProject(request)

    # Handle commands.
    domain = commands[0]

    if domain == 'run':
        run(commands[1:])
    elif domain == 'register':
        register(commands[1:])
    else:
        print(f'Error: Unrecognized command: "{domain}"')
