import argparse
import asyncio
import os

from bow_classifier import build as build_bow_classifier
from glove_classifier import build as build_glove_classifier
from utils import lifecycle
from utils.task_mgr import get_workflows, InvalidWorkflowName, register_workflows, run_workflow

_IMAGE_NAME = os.environ.get('IMAGE_NAME')
_PROJECT_NAME = os.environ.get('PROJECT_NAME')


def register(commands):
    if len(commands) > 0:
        print('Error: Invalid cli command.')
        exit(1)

    print('Registering Project...')
    lifecycle.start_connection()
    project = lifecycle.register_project()

    print(f'Project registered: {project.id}')


def run(commands):
    if len(commands) != 1:
        print('Error: Invalid cli command.')
        exit(1)

    workflow_name = commands[0]
    print(f'Running workflow: "{workflow_name}"...')

    lifecycle.start_connection()
    workflow_run = lifecycle.run_workflow(workflow_name)

    print(f'WorkflowRun ID: {workflow_run.id}')


def start(commands):
    if len(commands) > 0:
        print('Error: Invalid cli command.')
        exit(1)

    print('Starting worker...')
    lifecycle.start_connection()
    lifecycle.start_worker()
    worker = lifecycle.register_worker()

    print(f'Worker running: {worker.id}')


def info(commands):
    if len(commands) > 0:
        print('Error: Invalid cli command.')
        exit(1)

    print(f'Project Name: {_PROJECT_NAME}')
    print(f'Image Name: {_IMAGE_NAME}')


def tasks_ls(commands):
    if len(commands) > 0:
        print('Error: Invalid cli command.')
        exit(1)

    for executable in lifecycle.get_task_execs():
        routine_id = executable.routine_id
        print(routine_id.routine_name, '\t', routine_id.version)


def workflows_ls(commands):
    if len(commands) > 0:
        print('Error: Invalid cli command.')
        exit(1)

    for executable in lifecycle.get_workflow_execs():
        routine_id = executable.routine_id
        print(routine_id.routine_name)


def tmp(commands):
    async def run():
        lifecycle.start_local_job()
        hyperparams = [dict(lr=0.1), dict(lr=0.01), dict(lr=0.001)]
        model = await build_bow_classifier(epochs=2, hyperparams=hyperparams)
        print('Done building bow classifier')

    asyncio.run(run())


if __name__ == '__main__':
    register_workflows([build_bow_classifier, build_glove_classifier])

    parser = argparse.ArgumentParser(description='Project Runner')
    parser.add_argument('commands', type=str, nargs='+')

    args = parser.parse_args()
    commands = args.commands

    if len(commands) == 0:
        print('error: No commands provided.')
        exit(1)

    domain = commands[0]

    routines = {
        'tmp': tmp,
        'info': info,
        'register': register,
        'run': run,
        'start': start,
        'tasks ls': tasks_ls,
        'task ls': tasks_ls,
        't ls': tasks_ls,
        'ts ls': tasks_ls,
        'workflows ls': workflows_ls,
        'workflow ls': workflows_ls,
        'wf ls': workflows_ls,
        'wfs ls': workflows_ls,
    }

    found_match = False

    for key, func in routines.items():
        target = key.split()
        found_match = all(
            [x == y for x, y in zip(target, commands[:len(target)])])

        if found_match:
            func(commands[len(target):])
            break

    if not found_match:
        print(f'Error: Unrecognized command: "{domain}"')
        exit(1)
