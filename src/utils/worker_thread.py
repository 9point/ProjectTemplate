import threading
import time

from abc import ABC, abstractmethod

_IS_RUNNING = False
_LOOP_SECS = 5
_SUBSCRIBERS = []


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
    global _SUBSCRIBERS

    assert(_IS_RUNNING)

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


class Subscription:
    def __init__(self, subscriber):
        self.subscriber = subscriber

    def stop(self):
        global _SUBSCRIBERS

        sub = self.subscriber

        if sub in _SUBSCRIBERS:
            sub.will_stop()
            _SUBSCRIBERS.remove(sub)


def _start_thread_impl():
    global _IS_RUNNING
    global _SUBSCRIBERS
    global _LOOP_SECS

    assert(_IS_RUNNING)

    while _IS_RUNNING:
        for sub in _SUBSCRIBERS:
            sub.loop()

        time.sleep(_LOOP_SECS)
