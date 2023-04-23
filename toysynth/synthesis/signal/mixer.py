import logging
from copy import deepcopy

import numpy as np

from .component import Component
from .signal_type import SignalType

class Mixer(Component):
    def __init__(self, sample_rate, frames_per_chunk, subcomponents) -> None:
        super().__init__(sample_rate, frames_per_chunk, signal_type=SignalType.WAVE, subcomponents=subcomponents)
        self.log = logging.getLogger(__name__)

    def __iter__(self):
        self.subcomponent_iters = [iter(sub) for sub in self.subcomponents]
        return self
    
    def __next__(self):
        mix = np.zeros(self.frames_per_chunk, np.float32)

        if len(self.subcomponent_iters) <= 0:
            self.log.error("Had no subcomponents")
            return mix

        for sub in self.subcomponent_iters:
            mix += next(sub)
        
        return mix / len(self.subcomponent_iters)
    
    def __deepcopy__(self, memo):
        return Mixer(self.sample_rate, self.frames_per_chunk, subcomponents=[deepcopy(sub, memo) for sub in self.subcomponents])

        