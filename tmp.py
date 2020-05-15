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


loop = asyncio.new_event_loop()


def blah(loop):
    async def run(fut):
        await asyncio.sleep(2)
        fut.set_result(10)

    fut = loop.create_future()
    loop.create_task(run(fut))
    result = loop.run_until_complete(fut)
    print(result)


thread = threading.Thread(target=blah, args=(loop,))
thread.start()
print('running')
thread.join()
print('done')
