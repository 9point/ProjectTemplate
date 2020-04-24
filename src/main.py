import argparse
import os

from bow_classifier import train as train_bow_classifier
from utils.api import start_api
from utils.task_mgr import InvalidWorkflowName, register_workflows, run_workflow


def start(commands):
    if len(commands) > 0:
        print('Error: Invalid cli command.')
        exit(1)

    print('Starting api...')
    api = start_api()

    print('Registering project...')
    api.register_project()

    print('Registering worker...')
    api.register_worker()


def run(commands):
    if len(commands) != 1:
        print('Error: Invalid cli command.')
        exit(1)

    workflow_name = commands[0]
    print(f'Running workflow: "{workflow_name}"...')

    api = start_api()
    api.register_project()
    api.run_workflow()


if __name__ == '__main__':
    print('Registering Workflows...')
    register_workflows([train_bow_classifier])

    parser = argparse.ArgumentParser(description='Project Runner')
    parser.add_argument('commands', type=str, nargs='+')

    args = parser.parse_args()
    commands = args.commands

    if len(commands) == 0:
        print('error: No commands provided.')
        exit(1)

    domain = commands[0]

    routines = {
        'run': run,
        'start': start,
    }

    if domain not in routines:
        print(f'Error: Unrecognized command: "{domain}"')

    routines[domain](commands[1:])
