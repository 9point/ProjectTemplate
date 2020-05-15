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


async def run():
    print('running')
    result = await do_something()
    print(result)


def do_something():
    loop = asyncio.get_running_loop()
    fut = loop.create_future()

    async def do_fut():
        await asyncio.sleep(2)
        print('setting result')
        fut.set_result(10)

    loop.create_task(do_fut())

    return fut


asyncio.run(run())
