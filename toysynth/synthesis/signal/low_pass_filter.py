# import logging
# from copy import deepcopy

# import numpy as np

# from .component import Component
# from .signal_type import SignalType

# class LowPassFilter(Component):
#     """
#     TODO This component doesn't work right yet
#     """
#     def __init__(self, sample_rate, frames_per_chunk, source: Component, cutoff_frequency: float):
#         super().__init__(sample_rate, frames_per_chunk, signal_type=SignalType.WAVE)
#         self.log = logging.getLogger(__name__)
#         self.subcomponents = []
#         self.add_subcomponent(source)
#         self.cutoff_frequency = np.float32(cutoff_frequency)
#         self.alpha = self.compute_alpha()

#     def compute_alpha(self):
#         dt = 1 / self.sample_rate
#         rc = 1 / (2 * np.pi * self.cutoff_frequency)
#         return np.float32(dt / (rc + dt))

#     def __iter__(self):
#         self.source_iter = iter(self.subcomponents[0])
#         self.previous_output = np.zeros(self.frames_per_chunk, dtype=np.float32)
#         return self

#     def __next__(self):
#         input_signal = next(self.source_iter)
#         output_signal = self.alpha * input_signal + (1 - self.alpha) * np.roll(self.previous_output, 1)
#         self.previous_output = output_signal
#         return output_signal.astype(np.float32)
    
#     def __deepcopy__(self, memo):
#         return LowPassFilter(self.sample_rate, self.frames_per_chunk, deepcopy(self.subcomponents[0]), self.cutoff_frequency)
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
        self.cutoff_frequency = cutoff_frequency
        self.filter_order = filter_order
        self.sample_rate = sample_rate
        self.b, self.a = self.compute_coefficients()
        self.zi = self.compute_initial_conditions()

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
