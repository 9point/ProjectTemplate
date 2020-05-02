import inspect
import typing

from src.utils.introspection.runtime_typing import serialize_val


def joiner(l: typing.List[str]) -> str:
    return ' '.join(l)


def joiner_untyped(l):
    return ' '.join(l)


print(serialize_val(joiner))
# print(serialize_val(joiner_untyped))
