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
        num_active_voices = 0

        for sub in self.subcomponent_iters:
            (chunk, props) = next(sub)
            mix += chunk
            chunk_amp = props["amp"]
            if chunk_amp != 0:
                amp += chunk_amp
                num_active_voices += 1
        
        component_amp = (amp / num_active_voices) if num_active_voices > 0 else np.float32(0.0)
        self._props["amp"] = component_amp
        if amp > 1:
            mix = self.normalize_signal(mix)
        return (mix, self._props)
    
    def __deepcopy__(self, memo):
        return Mixer(self.sample_rate, self.frames_per_chunk, subcomponents=[deepcopy(sub, memo) for sub in self.subcomponents])
    

        