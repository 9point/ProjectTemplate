import inspect
import typing

# Much of this code is ported from here:
# https://github.com/ilevkivskyi/typing_inspect/blob/master/typing_inspect.py


def serialize_val(val):
    if inspect.isfunction(val):
        return serialize_type(inspect.signature(val))

    return _create_schema_unresolved(reason='MissingImpl')


def serialize_type(t):
    print(t)
    print('is empty:', _is_empty(t))

    if t is str:
        return _create_schema_primitive(name='String')

    if _is_empty(t):
        return _create_schema_unresolved(reason='MissingAnnotation')

    if type(t) is inspect.Signature:
        parameters = [serialize_type(p) for p in t.parameters.values()]

        return {
            'parameters': parameters,
            'return': serialize_type(t.return_annotation),
            'schemaType': 'Function',
            'type': 'Schema',
        }

    if type(t) is inspect.Parameter:
        return {
            'name': t.name,
            'schemaType': 'NamedSchema',
            'type': 'Schema',
            'value': serialize_type(t.annotation),
        }

    # Checking if this is a generic type. If so, what type of generic
    # is this?

    if _is_list(t):
        elements = [serialize_type(x) for x in t.__args__]

        return {
            'elements': elements,
            'schemaType': 'List',
            'type': 'Schema',
        }

    return _create_schema_unresolved(reason='MissingImpl')


def _create_schema_primitive(name):
    return {
        'name': name,
        'schemaType': 'Primitive',
        'type': 'Schema',
    }


def _create_schema_unresolved(reason):
    return {
        'reasonForUnresolved': reason,
        'schemaType': 'Unresolved',
        'type': 'Schema',
    }


def _is_empty(t):
    return isinstance(t, inspect._empty) or t is inspect.Signature.empty


def _is_iterable(t):
    return hasattr(t, '__iter__')


def _is_list(t):
    return _get_tgeneric(t) is list


def _get_tgeneric(t):
    # NOTE: Assuming python >= 3.7.0
    if isinstance(t, typing._GenericAlias):
        return t.__origin__ if t.__origin__ is not typing.ClassVar else None
    elif t is typing.Generic:
        return typing.Generic


# Copied from:
# https://github.com/ilevkivskyi/typing_inspect/blob/master/typing_inspect.py
def _get_generic_bases(tp):
    """Get generic base types of a type or empty tuple if not possible.
    Example::
        class MyClass(List[int], Mapping[str, List[int]]):
            ...
        MyClass.__bases__ == (List, Mapping)
        get_generic_bases(MyClass) == (List[int], Mapping[str, List[int]])
    """
    # return getattr(tp, '__orig_bases__', ())
    return getattr(tp, '__args__', ())
