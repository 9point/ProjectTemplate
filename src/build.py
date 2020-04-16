import os
import pkgutil

from importlib import import_module
from pathlib import Path

TASKFILE_SUFFIX = '_task.py'


def get_task_paths():
    # TODO: Need to check for task folders. In that case, need to look for the
    # __init__ method of a task folder.

    task_paths = []

    for root, _subdirs, files in os.walk(Path(__file__).parent):
        for file in files:
            if file.endswith(TASKFILE_SUFFIX):
                task_paths.append(os.path.join(root, file))

    return task_paths


def main():
    task_paths = get_task_paths()
    print(task_paths)


if __name__ == '__main__':
    main()
