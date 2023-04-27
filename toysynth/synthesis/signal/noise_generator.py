import logging
from copy import deepcopy

import numpy as np

from .generator import Generator
from .signal_type import SignalType

class NoiseGenerator(Generator):
    def __init__(self, sample_rate, frames_per_chunk, name="Noise Generator"):
        super().__init__(sample_rate, frames_per_chunk, signal_type=SignalType.WAVE, name=name)
        self.log = logging.getLogger(__name__)
        self._props["amp"] = 1.0


    def __iter__(self):
        return super().__iter__()
    
    def __next__(self):
        if self.active:
            rng = np.random.default_rng()
            noise = rng.uniform(-1.0, 1.0, self.frames_per_chunk)
            self._props["amp"] = 1.0
            return (noise.astype(np.float32), self._props)
        else:
            self._props["amp"] = 0.0
            return (np.zeros(self.frames_per_chunk, dtype=np.float32), self._props)
    
    def __deepcopy__(self, memo):
        return NoiseGenerator(self.sample_rate, self.frames_per_chunk)