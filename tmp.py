# import inspect
# import typing

# from src.utils.introspection.typing import serialize


# def joiner(l: typing.List[str]) -> str:
#     return ' '.join(l)


# def joiner_untyped(l):
#     return ' '.join(l)


# def plus(a: float, b: float) -> float:
#     return a + b


# def return_void(a: float, b: str) -> None:
#     print(a, b)


# # print(serialize.from_val(joiner))
# # print(serialize.from_val(return_void))
# print(serialize.from_val(None))
# # print(serialize.from_val(joiner_untyped))

import time
import threading
import queue


class Foo:
    def __init__(self):
        self.q = queue.Queue()

    def start(self):
        a = threading.Thread(target=self._get)
        b = threading.Thread(target=self._put)
        a.start()
        b.start()

    def _get(self):
        while True:
            i = self.q.get(block=True)
            print('Getting', i)

    def _put(self):
        i = 0
        while True:
            time.sleep(1)
            i += 1
            self.q.put(i)
            print('Putting', i)


foo = Foo()
foo.start()
