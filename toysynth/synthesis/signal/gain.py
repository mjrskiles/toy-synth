import logging
from copy import deepcopy
from typing import List

import numpy as np

from .component import Component
from .signal_type import SignalType

class Gain(Component):
    """
    A gain component multiplies the amplitude of the signal by a constant factor.
    """
    def __init__(self, sample_rate, frames_per_chunk, signal_type: SignalType, subcomponents: List['Component'] = [], name="Gain", control_tag="gain"):
        super().__init__(sample_rate, frames_per_chunk, signal_type, subcomponents, name)
        self.log = logging.getLogger(__name__)
        self.amp = 1.0
        self.control_tag = control_tag

    def __iter__(self):
        self.subcomponent_iter = iter(self.subcomponents[0])
        return self
    
    def __next__(self):
        (chunk, props) = next(self.subcomponent_iter)
        props["amp"] *= self.amp
        return (chunk * self.amp, props)
    
    def __deepcopy__(self, memo):
        return Gain(self.sample_rate, self.frames_per_chunk, self.signal_type, subcomponents=[deepcopy(self.subcomponents[0], memo)], name=self.name, control_tag=self.control_tag)
    
    @property
    def amp(self):
        return self._amp
    
    @amp.setter
    def amp(self, value):
        try:
            float_val = float(value)
            if float_val > 1.0 or float_val < 0.0:
                raise ValueError
            self._amp = float_val
        except ValueError:
            self.log.error(f"Gain must be between 0.0 and 1.0, got {value}")