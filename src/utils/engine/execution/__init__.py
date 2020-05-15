import threading

_LOCAL_RUN_ID = 1
_LOCAL_RUN_ID_LOCK = threading.Lock()


def create_local_run_id():
    global _LOCAL_RUN_ID
    global _LOCAL_RUN_ID_LOCK

    with _LOCAL_RUN_ID_LOCK:
        local_id = _LOCAL_RUN_ID
        _LOCAL_RUN_ID += 1

    return str(local_id)
