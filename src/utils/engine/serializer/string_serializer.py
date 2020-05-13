from .serializer import Serializer as BaseSerializer


class Serializer(BaseSerializer):
    @property
    def key(self):
        return 'v1.string'

    def claim_val(self, val):
        return type(val) is str

    def serialize(self, serialize_func, val):
        return dict(key=self.key, val=val)

    def deserialize(self, deserialize_func, serial):
        assert 'key' in serial
        assert 'val' in serial
        assert serial['key'] == self.key
        return serial['val']
