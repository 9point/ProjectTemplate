import argparse
import os

from bow_classifier import train as build_bow_classifier
from glove_classifier import build as build_glove_classifier
from utils import lifecycle
from utils.task_mgr import get_workflows, InvalidWorkflowName, register_workflows, run_workflow


def start(commands):
    if len(commands) > 0:
        print('Error: Invalid cli command.')
        exit(1)

    print('Starting worker...')
    lifecycle.start_connection()
    lifecycle.start_worker()
    worker = lifecycle.register_worker()

    print(f'Worker running: {worker.id}')


def run(commands):
    if len(commands) != 1:
        print('Error: Invalid cli command.')
        exit(1)

    workflow_name = commands[0]
    print(f'Running workflow: "{workflow_name}"...')

    lifecycle.start_connection()
    workflow_run = lifecycle.run_workflow(workflow_name)

    print(f'WorkflowRun ID: {workflow_run.id}')


def register(commands):
    if len(commands) > 0:
        print('Error: Invalid cli command.')
        exit(1)

    print('Registering Project...')
    lifecycle.start_connection()
    project = lifecycle.register_project()

    print(f'Project registered: {project.id}')


if __name__ == '__main__':
    register_workflows([build_bow_classifier, build_glove_classifier])

    for wf in get_workflows():
        print(wf.name)
        print(wf.call_graph)

    parser = argparse.ArgumentParser(description='Project Runner')
    parser.add_argument('commands', type=str, nargs='+')

    args = parser.parse_args()
    commands = args.commands

    if len(commands) == 0:
        print('error: No commands provided.')
        exit(1)

    domain = commands[0]

    routines = {
        'register': register,
        'run': run,
        'start': start,
    }

    if domain not in routines:
        print(f'Error: Unrecognized command: "{domain}"')

    routines[domain](commands[1:])
