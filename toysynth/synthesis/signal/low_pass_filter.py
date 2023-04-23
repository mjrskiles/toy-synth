import logging
from copy import deepcopy

import numpy as np
from scipy.signal import butter, lfilter, lfilter_zi

from .component import Component
from .signal_type import SignalType

class LowPassFilter(Component):
    def __init__(self, sample_rate, frames_per_chunk, source: Component, cutoff_frequency: float, filter_order: int = 2):
        super().__init__(sample_rate, frames_per_chunk, signal_type=SignalType.WAVE)
        self.log = logging.getLogger(__name__)
        self.subcomponents = []
        self.add_subcomponent(source)
        self.filter_order = filter_order
        self.sample_rate = sample_rate
        self.cutoff_frequency = cutoff_frequency
        self.b, self.a = self.compute_coefficients()
        self.zi = self.compute_initial_conditions()

    @property
    def cutoff_frequency(self):
        return self._cutoff_frequency
    
    @cutoff_frequency.setter
    def cutoff_frequency(self, value):
        try:
            float_val = float(value)
            if float_val < 0.0:
                raise ValueError("Cutoff frequency must be positive.")
            self._cutoff_frequency = float_val
            self.b, self.a = self.compute_coefficients()
        except ValueError:
            self.log.error(f"Couldn't set with value {value}")

    def compute_coefficients(self):
        nyquist = 0.5 * self.sample_rate
        normalized_cutoff = self.cutoff_frequency / nyquist
        b, a = butter(self.filter_order, normalized_cutoff, btype='low', analog=False)
        return b, a

    def compute_initial_conditions(self):
        zi = lfilter_zi(self.b, self.a)
        return zi

    def __iter__(self):
        self.source_iter = iter(self.subcomponents[0])
        return self

    def __next__(self):
        input_signal = next(self.source_iter)
        output_signal, self.zi = lfilter(self.b, self.a, input_signal, zi=self.zi)
        return output_signal.astype(np.float32)

    def __deepcopy__(self, memo):
        return LowPassFilter(self.sample_rate, self.frames_per_chunk, deepcopy(self.subcomponents[0]), self.cutoff_frequency, self.filter_order)
