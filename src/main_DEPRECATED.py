import argparse
import os

from bow_classifier import train as train_bow_classifier
from utils.api import start_api
from utils.task_mgr import InvalidWorkflowName, register_workflows, run_workflow


def run(commands):
    if len(commands) == 0:
        print('Error: Must provide task name to run.')
        exit(1)

    workflow_name = commands[0]
    print(f'Running command: "{workflow_name}"...')

    api = start_api()
    api.register_worker()


def register(commands):
    print('Registering Project...')
    api = start_api()
    api.register_project()


if __name__ == '__main__':
    register_workflows([train_bow_classifier])

    parser = argparse.ArgumentParser(description='Project Runner')
    parser.add_argument('commands', type=str, nargs='+')

    args = parser.parse_args()
    commands = args.commands

    if len(commands) == 0:
        print('error: No commands provided.')
        exit(1)

    # Handle commands.
    domain = commands[0]

    if domain == 'run':
        run(commands[1:])
    elif domain == 'register':
        register(commands[1:])
    else:
        print(f'Error: Unrecognized command: "{domain}"')
