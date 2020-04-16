import argparse

from tasks.mnist_task import mnist
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
    register_tasks([mnist])

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
