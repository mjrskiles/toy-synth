import logging
from copy import deepcopy
from typing import List

import numpy as np

from .component import Component
from .signal_type import SignalType

class Gain(Component):
    """
    A gain component multiplies the amplitude of the signal by a constant factor.
    TODO finish and test this component
    """
    def __init__(self, sample_rate, frames_per_chunk, signal_type: SignalType, subcomponents: List['Component'] = [], name="Component"):
        super().__init__(sample_rate, frames_per_chunk, signal_type, subcomponents, name)
        self.log = logging.getLogger(__name__)

    def __iter__(self):
        self.subcomponent_iter = iter(self.subcomponents[0])
        return self
    
    def __next__(self):
        (chunk, props) = next(self.subcomponent_iter)
        return (chunk * self.amp, props)