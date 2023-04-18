import logging

import numpy as np

from .component import Component
from .signal_type import SignalType
from . import utils

class DualMixer(Component):
    def __init__(self, sample_rate, frames_per_chunk, input_a: Component, input_b: Component, amp_a: Component, amp_b: Component) -> None:
        super().__init__(sample_rate, frames_per_chunk, signal_type=SignalType.WAVE)
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
            inp_arr = next(self._input_iters[i])
            amp_arr = next(self._amp_iters[i])

            # If the signal type is WAVE that means the range is [-1, 1], which means
            # we need to convert to [0, 1]
            if self.amps[i].signal_type == SignalType.WAVE:
                mapped = map(utils.squish, amp_arr)
                amp_arr = np.array(list(mapped), dtype=np.float32) # TODO can this be faster?
                
            amp_applied = np.prod([inp_arr, amp_arr], axis=0)
            amped.append(amp_applied)
        summed = np.sum(amped, axis=0) / num_inputs
        return summed
    
