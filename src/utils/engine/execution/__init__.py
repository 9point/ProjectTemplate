import threading

_LOCAL_EXECUTION_ID = 1
_LOCAL_EXECUTION_ID_LOCK = threading.Lock()


def create_execution_id():
    global _LOCAL_EXECUTION_ID
    global _LOCAL_EXECUTION_ID_LOCK

    with _LOCAL_EXECUTION_ID_LOCK:
        local_id = _LOCAL_EXECUTION_ID
        _LOCAL_EXECUTION_ID += 1

    return local_id
