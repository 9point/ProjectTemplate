import os
import pkgutil

from importlib import import_module
from pathlib import Path


def splitall(path):
    allparts = []
    while 1:
        parts = os.path.split(path)
        if parts[0] == path:  # sentinel for absolute paths
            allparts.insert(0, parts[0])
            break
        elif parts[1] == path:  # sentinel for relative paths
            allparts.insert(0, parts[1])
            break
        else:
            path = parts[0]
            allparts.insert(0, parts[1])
    return allparts


def get_import_paths():
    # TODO: Need to check for task folders. In that case, need to look for the
    # __init__ method of a task folder.

    import_paths = []

    self_file = Path(__file__)
    slice_count = len(os.path.split(__file__)) - 1

    for root, _subdirs, files in os.walk(self_file.parent):
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                import_path = os.path.join(*splitall(full_path)[slice_count:])[:-3]
                import_paths.append(import_path)

    return [p.replace('/', '.') for p in import_paths]


def main():
    import_paths = get_import_paths()
    for path in import_paths:
        import_module(path, package=__name__)


if __name__ == '__main__':
    main()
