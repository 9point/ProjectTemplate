from .collection_serializer import Serializer as CollectionSerializer
from .numeric_serializer import Serializer as NumericSerializer
from .string_serializer import Serializer as StringSerializer

_SERIALIZERS = [
    NumericSerializer(),
    StringSerializer(),
    CollectionSerializer(),
]


def serialize(val):
    for s in _SERIALIZERS:
        if s.claim_val(val):
            return s.serialize(serialize_func=serialize, val=val)

    raise NoAvailableSerializer()


def deserialize(serial):
    for s in _SERIALIZERS:
        if s.claim_serial(serial):
            return s.deserialize(deserialize_func=deserialize, serial=serial)

    raise UnknownSerializerKey()


class NoAvailableSerializer(Exception):
    pass


class BadSerialization(Exception):
    pass


class UnknownSerializerKey(Exception):
    pass
