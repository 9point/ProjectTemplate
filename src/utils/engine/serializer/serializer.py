from abc import ABC, abstractclassmethod, abstractmethod


class Serializer(ABC):
    @property
    @abstractmethod
    def key(self):
        pass

    @abstractmethod
    def claim_val(self, val):
        pass

    def claim_serial(self, serial):
        return 'key' in serial and serial['key'] == self.key

    @abstractmethod
    def serialize(self, serialize_func, val):
        pass

    @abstractmethod
    def deserialize(self, deserialize_func, serial):
        pass
