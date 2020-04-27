import argparse
import os

from bow_classifier import train as train_bow_classifier
from utils import lifecycle
from utils.task_mgr import InvalidWorkflowName, register_workflows, run_workflow


def start(commands):
    if len(commands) > 0:
        print('Error: Invalid cli command.')
        exit(1)

    print('Starting api...')
    lifecycle.start()
    lifecycle.register_project()
    lifecycle.register_worker()


def run(commands):
    if len(commands) != 1:
        print('Error: Invalid cli command.')
        exit(1)

    workflow_name = commands[0]
    print(f'Running workflow: "{workflow_name}"...')

    lifecycle.start()
    lifecycle.register_project()
    lifecycle.run_workflow(workflow_name)


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
