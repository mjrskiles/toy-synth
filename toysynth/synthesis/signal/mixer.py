import logging
from copy import deepcopy

import numpy as np

from .component import Component
from .signal_type import SignalType
from . import utils

class Mixer(Component):
    def __init__(self, sample_rate, frames_per_chunk, subcomponents, name="Mixer") -> None:
        super().__init__(sample_rate, frames_per_chunk, signal_type=SignalType.WAVE, subcomponents=subcomponents, name=name)
        self.log = logging.getLogger(__name__)

    def __iter__(self):
        self.subcomponent_iters = [iter(sub) for sub in self.subcomponents]
        return self
    
    def __next__(self):
        mix = np.zeros(self.frames_per_chunk, np.float32)
        amp = 0.0

        if len(self.subcomponent_iters) <= 0:
            self.log.error("Had no subcomponents")
            return mix

        for sub in self.subcomponent_iters:
            (chunk, props) = next(sub)
            mix += chunk
            amp += props["amp"]
        
        # self.log.debug(f"Mix max was {mix.max()}, min was {mix.min()}")
        
        self._props["amp"] = amp
        if amp != 0:
            mix = mix / np.float32(amp)
        return (mix, self._props)
    
    def __deepcopy__(self, memo):
        return Mixer(self.sample_rate, self.frames_per_chunk, subcomponents=[deepcopy(sub, memo) for sub in self.subcomponents])

        