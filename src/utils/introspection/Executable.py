from abc import ABC, abstractmethod


class Executable(ABC):
    def __init__(self, e_type):
        self.e_type = e_type
