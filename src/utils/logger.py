import datetime

from utils import lifecycle

_ORDER = 0


def write(*args):
    global _ORDER

    str = ' '.join(args)
    payload = {'i': ['describable'],
               'descriptor': str,
               'order': _ORDER}

    lifecycle.send_directive('v1.log', payload)

    print(*args)
    _ORDER += 1
