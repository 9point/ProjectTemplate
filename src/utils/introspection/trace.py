
_TRACE_STACK = []


def current_trace():
    global _TRACE_STACK

    if len(_TRACE_STACK) == 0:
        return None

    return _TRACE_STACK[-1]


class trace:
    def __init__(self):
        self._trace = None

    def __enter__(self):
        global _TRACE_STACK

        assert(self._trace is None)

        self._trace = Trace()

        _TRACE_STACK.append(self._trace)
        return self._trace

    def __exit__(self, exc_type, exc_value, traceback):
        global _TRACE_STACK
        # TODO: Properly handle errors.

        if self._trace is None:
            return

        assert(self._trace is _TRACE_STACK[-1])
        _TRACE_STACK.pop(-1)


class Trace:
    def __init__(self):
        self._executable = None

    def visit(self, executable):
        self._executable = executable
