import inspect
import typing

# Much of this code is ported from here:
# https://github.com/ilevkivskyi/typing_inspect/blob/master/typing_inspect.py


_T_PRIMITIVES = {'Bool': bool, 'Float': float, 'Int': int, 'String': str}


def from_val(val):

    if _is_val_primitive(val):
        return from_type(type(val))

    elif val is None:
        return _create_schema_primitive(name='Nil')

    elif inspect.isfunction(val):
        return from_type(inspect.signature(val))

    return _create_schema_unresolved(reason='MissingImpl')


def from_type(t, interpret_none_as_void=False):
    print(t)

    # TODO: Should include byte sizes for float and int types.
    if _is_type_primitive(t):
        for _k, _t in _T_PRIMITIVES.items():
            if _t is t:
                return _create_schema_primitive(name=_k)

    if t is None:
        return _create_schema_void() if interpret_none_as_void else _create_schema_primitive(name='Nil')

    if _is_type_empty(t):
        return _create_schema_unresolved(reason='MissingAnnotation')

    if type(t) is inspect.Signature:
        parameters = [
            from_type(p) for p in t.parameters.values()]

        return {
            'parameters': parameters,
            'return': from_type(t.return_annotation,
                                                    interpret_none_as_void=True),
            'schemaType': 'Function',
            'type': 'Schema',
        }

    if type(t) is inspect.Parameter:
        return {
            'name': t.name,
            'schemaType': 'NamedSchema',
            'type': 'Schema',
            'value': from_type(t.annotation),
        }

    # Checking if this is a generic type. If so, what type of generic
    # is this?

    if _is_type_list(t):
        elements = [from_type(x) for x in t.__args__]

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


def _create_schema_void():
    return {
        'scheaType': 'Void',
        'type': 'Schema',
    }


def _create_schema_unresolved(reason):
    return {
        'reasonForUnresolved': reason,
        'schemaType': 'Unresolved',
        'type': 'Schema',
    }


def _is_val_primitive(v):
    return any([type(v) is t for t in _T_PRIMITIVES.values()])


def _is_type_primitive(t):
    return any(t is _t for _t in _T_PRIMITIVES.values())


def _is_type_empty(t):
    return isinstance(t, inspect._empty) or t is inspect.Signature.empty


def _is_type_iterable(t):
    return hasattr(t, '__iter__')


def _is_type_list(t):
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
