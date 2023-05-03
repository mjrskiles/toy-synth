import logging
from copy import deepcopy

import numpy as np

from .generator import Generator
from .signal_type import SignalType

class ConstantValueGenerator(Generator):
    def __init__(self, sample_rate, frames_per_chunk, value=1.0, name="ConstantValueGenerator"):
        super().__init__(sample_rate, frames_per_chunk, signal_type=SignalType.AMP, name=name)
        self.log = logging.getLogger(__name__)
        self.value = value
        self._props["amp"] = 1.0

    @property
    def value(self):
        """The constant value to generate"""
        return self._value
    
    @value.setter
    def value(self, new_value):
        try:
            float_value = float(new_value)
            if float_value >= -1.0 and float_value <= 1.0:
                self._value = float_value
            else:
                raise ValueError(f"Value {new_value} is not between -1.0 and 1.0")
        except ValueError:
            self.log.error(f"Unable to set with value {new_value}")

    def __iter__(self):
        return super().__iter__()
    
    def __next__(self):
        arr = np.full(self.frames_per_chunk, self.value, dtype=np.float32)
        return (arr, self._props)

    def __deepcopy__(self, memo):
        return ConstantValueGenerator(self.sample_rate, self.frames_per_chunk, self.value)
