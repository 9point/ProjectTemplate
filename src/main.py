import argparse
import grpc

from static_codegen import mlservice_pb2, mlservice_pb2_grpc
from tasks.test import test_task
from utils.task_mgr import InvalidTaskName, register_tasks, run_task


def run(commands):
    if len(commands) == 0:
        print('Error: Must provide task name to run.')
        exit(1)

    task_name = commands[0]
    print(f'Running command: "{task_name}"...')

    try:
        run_task(task_name)
    except InvalidTaskName:
        print(f'Error: Invalid task name: "{task_name}"')
        exit(1)


def register(commands):
    print('Registering Project...')


if __name__ == '__main__':

    # print('Connecting to grpc...')
    # channel = grpc.insecure_channel('localhost:50051')
    # stub = mlservice_pb2_grpc.MLServiceStub(channel)

    # request = mlservice_pb2.Req_MLProjects()
    # for response in stub.GetProjects(request):
    #     print(response)

    register_tasks([test_task])

    parser = argparse.ArgumentParser(description='Project Runner')
    parser.add_argument('commands', type=str, nargs='+')

    args = parser.parse_args()
    commands = args.commands

    if len(commands) == 0:
        print('error: No commands provided.')
        exit(1)

    domain = commands[0]

    if domain == 'run':
        run(commands[1:])
    elif domain == 'register':
        register(commands[1:])
    else:
        print(f'Error: Unrecognized command: "{domain}"')
