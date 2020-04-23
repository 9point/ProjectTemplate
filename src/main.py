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
    print('Registering Workflows...')

    register_workflows([train_bow_classifier])

    print('Starting api...')
    api = start_api()

    print('Registering project...')
    api.register_project()

    print('Registering worker...')
    api.register_worker()
