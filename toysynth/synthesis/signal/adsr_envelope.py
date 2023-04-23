import logging
from copy import deepcopy
from enum import Enum

import numpy as np

from .component import Component
from .signal_type import SignalType

class AdsrEnvelope(Component):
    class State(Enum):
        IDLE = 0
        ATTACK = 1
        DECAY = 2
        SUSTAIN = 3
        RELEASE = 4

    def __init__(self, sample_rate, frames_per_chunk, source: Component):
        super().__init__(sample_rate, frames_per_chunk, signal_type=SignalType.WAVE)
        self.add_subcomponent(source)
        self.attack = 0.5
        self.decay = 0.8
        self.sustain = 0.6
        self.release = 0.5
        self.state = AdsrEnvelope.State.IDLE

    def __iter__(self):
        self.source_iter = iter(self.subcomponents[0])
        return self
    
    def __next__(self):
        source_chunk = next(self.source_iter)
        if not self.active:
            return np.zeros_like(source_chunk)
        
        match self.state:
            case AdsrEnvelope.State.IDLE:
                pass

        
    def __deepcopy__(self, memo):
        return AdsrEnvelope(self.sample_rate, self.frames_per_chunk, deepcopy(self.subcomponents[0]))