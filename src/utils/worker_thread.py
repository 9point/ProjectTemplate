import threading
import time

from abc import ABC, abstractmethod

_IS_RUNNING = False
_LAST_CALL_SECS = []
_LOOP_SECS = 5
_MIN_LOOP_SECS = []
_SUBSCRIBERS = []

# This lock is used to update the list of subscribers. The _LAST_CALL_SECS,
# _LOOP_SECS, and _SUBSCRIBERS lists all need to be kept in sync. For this
# reason, a lock is used so that these properties can be managed.

# TODO: Think through some lock-free mechanisms for managing this. Maybe
# creating a single list with all the subscriber metadata as an object can be
# a more efficient approach to this.
_SUBSCRIBER_WRITE_LOCK = threading.Lock()


def start_thread():
    global _IS_RUNNING

    assert(not _IS_RUNNING)

    _IS_RUNNING = True
    thread = threading.Thread(target=_start_thread_impl)
    thread.start()


def stop_thread():
    global _IS_RUNNING

    assert(_IS_RUNNING)

    _IS_RUNNING = False


def add_subscriber(subscriber):
    global _IS_RUNNING
    global _LAST_CALL_SECS
    global _MIN_LOOP_SECS
    global _SUBSCRIBER_WRITE_LOCK
    global _SUBSCRIBERS

    assert(_IS_RUNNING)

    with _SUBSCRIBER_WRITE_LOCK:
        _LAST_CALL_SECS.append(0)
        _MIN_LOOP_SECS.append(subscriber.minimum_loop_time_secs())
        _SUBSCRIBERS.append(subscriber)

    subscriber.did_start()
    return Subscription(subscriber)


class Subscriber(ABC):
    @abstractmethod
    def loop(self):
        pass

    @abstractmethod
    def did_start(self):
        pass

    @abstractmethod
    def will_stop(self):
        pass

    @abstractmethod
    def minimum_loop_time_secs(self):
        """
        When a subscriber subscribes to the worker thread and it is getting
        called on the event loop, the subscriber needs to specify a minimum
        amount of time between loops. This is for performance reasons. If,
        for example, 30 seconds is returned, then the shortest amount of time
        allowed from one loop call to the next will be 30 seconds.

        Note that this value is dynamic. After the loop call of the subscriber
        is called, the minimum loop time is re-queried on the subscriber.
        This allows the subscriber to dynamically adjust their minimum
        loop time as needed.
        """
        pass


class Subscription:
    def __init__(self, subscriber):
        self.subscriber = subscriber

    def stop(self):
        global _LAST_CALL_SECS
        global _MIN_LOOP_SECS
        global _SUBSCRIBER_WRITE_LOCK
        global _SUBSCRIBERS

        sub = self.subscriber

        if sub in _SUBSCRIBERS:
            sub.will_stop()

            with _SUBSCRIBER_WRITE_LOCK:
                idx = _SUBSCRIBERS.index(sub)

                _LAST_CALL_SECS.remove(_LAST_CALL_SECS[idx])
                _MIN_LOOP_SECS.remove(_MIN_LOOP_SECS[idx])
                _SUBSCRIBERS.remove(sub)


def _start_thread_impl():
    global _IS_RUNNING
    global _LAST_CALL_SECS
    global _LOOP_SECS
    global _MIN_LOOP_SECS
    global _SUBSCRIBER_WRITE_LOCK
    global _SUBSCRIBERS

    assert(_IS_RUNNING)
    assert(len(_SUBSCRIBERS) == len(_LAST_CALL_SECS))
    assert(len(_SUBSCRIBERS) == len(_MIN_LOOP_SECS))

    while _IS_RUNNING:
        # NOTE: This now value is used to measure if each subscriber is ready
        # to get executed. Note that because this time is taken before loop
        # calls and there is no way of knowing that each subscriber will
        # complete in a reasonable amount of time, this value may not be
        # totally accurate. However, this is a good enough approximation for
        # determining how much time has passed since each subscribers
        # last execution.
        now = time.time()

        for i, sub in enumerate(_SUBSCRIBERS):
            last_call = _LAST_CALL_SECS[i]
            min_time_secs = _MIN_LOOP_SECS[i]

            # Enough time has passed since we last called this subscriber.
            # Call it again and update the loop time records.
            if (now - last_call) >= min_time_secs:
                sub.loop()

                with _SUBSCRIBER_WRITE_LOCK:
                    _LAST_CALL_SECS[i] = now
                    _MIN_LOOP_SECS[i] = sub.minimum_loop_time_secs()

        time.sleep(_LOOP_SECS)
