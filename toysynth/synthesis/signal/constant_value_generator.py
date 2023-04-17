import logging

import numpy as np

from .generator import Generator

class ConstantValueGenerator(Generator):
    def __init__(self, sample_rate, frames_per_chunk, value=1.0):
        super().__init__(sample_rate, frames_per_chunk)
        self.log = logging.getLogger(__name__)
        self.value = value

    @property
    def value(self):
        """The constant value to generate"""
        return self._value
    
    @value.setter
    def value(self, new_value):
        try:
            self._value = float(new_value)
        except ValueError:
            self.log.error(f"Unable to set with value {new_value}")

    def __iter__(self):
        return super().__iter__()
    
    def __next__(self):
        arr = np.full(self.frames_per_chunk, self.value, dtype=np.float32)
        return arr

