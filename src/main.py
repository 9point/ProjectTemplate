import argparse
import bow_classifier
import glove_classifier
import json
import os
import simple_example

from utils import lifecycle
from utils.RoutineID import RoutineID


def register():
    lifecycle.start_connection()
    project = lifecycle.register_project()
    print(f'Finished registering project: {project.id}')


def info():
    # Get container image name
    # Get project name
    # Get routine ids
    pass


def start_worker():
    print('Starting worker')
    lifecycle.start_connection()
    worker = lifecycle.register_worker(accepts_work_requests=True)
    print(f'Registered Worker: {worker.id}')

    lifecycle.start_engine()


def deploy(payload):
    # TODO: IMPLEMENT ME
    # Register the project, routines, and container with the service.
    # Deploy using the deployment params provided.
    pass


def run_local(payload):
    assert 'arguments' in payload
    assert 'connect' in payload
    assert 'routineID' in payload

    arguments = payload['arguments']
    connect = payload['connect']
    routine_id = RoutineID.parse(payload['routineID'])
    executable = lifecycle.get_exec(routine_id)

    if connect:
        print('Connecting to service...')
        lifecycle.start_connection()
        worker = lifecycle.register_worker(accepts_work_requests=False)
        print(f'Registered worker: {worker.id}')

    result = lifecycle.start_local_routine(executable, arguments)
    print('done')
    # print(result)


def run_remote(payload):
    # Execute the routine remotely.
    lifecycle.start_connection()
    run = lifecycle.start_remote_routine(simple_example.build)
    print('Starting run:', run.id)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Project")
    parser.add_argument('command')
    parser.add_argument('--file')

    args = parser.parse_args()

    if args.command == 'start-worker':
        start_worker()
        exit(0)

    if args.command == 'register':
        register()
        exit(0)

    if args.command == 'run-local':
        assert args.file is not None
        payload_path = os.path.join(os.getcwd(), args.file)

        with open(payload_path, 'r') as file:
            content = file.read()

        payload = json.loads(content)
        run_local(payload)
        exit(0)

    print('Bad command')
    exit(1)
