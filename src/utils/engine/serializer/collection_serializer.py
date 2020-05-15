from .numeric_serializer import Serializer as NumericSerializer
from .string_serializer import Serializer as StringSerializer
from .serializer import Serializer as BaseSerializer


class Serializer(BaseSerializer):
    @property
    def key(self):
        return 'v1.Collection'

    def claim_val(self, val):
        return type(val) in [list, dict, set, tuple]

    def serialize(self, serialize_func, val):
        if type(val) is list:
            serial_val = [serialize_func(v) for v in val]
            return dict(key=self.key, collection_type='list', val=serial_val)

        if type(val) is dict:
            # TODO: Assuming key is always a string. Need to address this later.
            serial_val = {k: serialize_func(v) for k, v in val.items()}
            return dict(key=self.key, collection_type='dict', val=serial_val)

        if type(val) is tuple:
            serial_val = [serialize_func(v) for v in val]
            return dict(key=self.key, collection_type='tuple', val=serial_val)

        assert False

    def deserialize(self, deserialize_func, serial):
        assert 'key' in serial
        assert 'val' in serial
        assert 'collection_type' in serial
        assert serial['key'] == self.key
        serial_val = serial['val']

        if serial['collection_type'] == 'list':
            return [deserialize_func(sv) for sv in serial_val]

        if serial['collection_type'] == 'dict':
            return {k: deserialize_func(sv) for k, sv in serial_val.items()}

        if serial['collection_type'] == 'tuple':
            return tuple([deserialize_func(sv) for sv in serial_val])

        assert False
