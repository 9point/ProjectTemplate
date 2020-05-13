from .serializer import Serializer as BaseSerializer


class Serializer(BaseSerializer):
    @property
    def key(self):
        return 'v1.numeric'

    def claim_val(self, val):
        return type(val) in [int, float]

    def serialize(self, serialize_func, val):
        return dict(key=self.key, val=val)

    def deserialize(self, deserialize_func, serial):
        assert 'val' in serial
        assert 'key' in serial
        assert self.key == serial['key']

        return serial['val']
