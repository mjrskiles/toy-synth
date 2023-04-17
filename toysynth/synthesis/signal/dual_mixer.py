import logging

import numpy as np

from .component import Component

from .noise_generator import NoiseGenerator

class DualMixer(Component):
    def __init__(self, sample_rate, frames_per_chunk, input_a: Component, input_b: Component, amp_a: Component, amp_b: Component) -> None:
        super().__init__(sample_rate, frames_per_chunk)
        self.log = logging.getLogger(__name__)
        self.inputs = [input_a, input_b]
        self.amps = [amp_a, amp_b]

    def __iter__(self):
        self._input_iters = [iter(inp) for inp in self.inputs]
        self._amp_iters = [iter(amp) for amp in self.amps]
        return self
    
    def __next__(self):
        num_inputs = len(self.inputs)
        amped = []
        for i in range(num_inputs):
            amp_applied = np.prod([next(self._input_iters[i]) * next(self._amp_iters[i])], axis=0)
            amped.append(amp_applied)
        summed = np.sum(amped, axis=0) / num_inputs
        return summed
    
