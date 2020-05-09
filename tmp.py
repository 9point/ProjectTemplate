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

import asyncio
import threading
import time
import queue

q = queue.Queue()


def start_loop(q):
    print('starting loop')
    loop = asyncio.new_event_loop()
    task = loop.create_task(run('main thread', q))
    loop.run_forever()


async def run(message, q):
    i = 0
    while True:
        q.put(f'{message} {i}')
        i += 1
        time.sleep(1)


def process(q: queue.Queue):
    while True:
        message = q.get(block=True)
        print('Processing message', message)


thread = threading.Thread(target=process, args=(q,))
thread.start()

start_loop(q)
