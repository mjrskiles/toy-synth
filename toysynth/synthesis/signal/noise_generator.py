import logging

import numpy as np

from .generator import Generator
from .signal_type import SignalType

class NoiseGenerator(Generator):
    def __init__(self, sample_rate, frames_per_chunk):
        super().__init__(sample_rate, frames_per_chunk, signal_type=SignalType.WAVE)
        self.log = logging.getLogger(__name__)

    def __iter__(self):
        return super().__iter__()
    
    def __next__(self):
        rng = np.random.default_rng()
        noise = rng.uniform(-1.0, 1.0, self.frames_per_chunk)
        return noise.astype(np.float32)