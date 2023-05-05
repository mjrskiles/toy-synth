import logging
from copy import deepcopy

import numpy as np

from .component import Component
from .signal_type import SignalType

class Delay(Component):
    def __init__(self, sample_rate, frames_per_chunk, subcomponents, name="Delay", delay_time=0.2) -> None:
        super().__init__(sample_rate, frames_per_chunk, signal_type=SignalType.WAVE, subcomponents=subcomponents, name=name)
        self.log = logging.getLogger(__name__)
        self.delay_time = delay_time
        self.delay_frames = int(self.delay_time * self.sample_rate)
        self.log.debug(f"Delay frames: {self.delay_frames}")
        self.delay_buffer = np.zeros(self.delay_frames, np.float32)
        self.delay_buffer_index = 0
        self.wet_gain = 0.5 

    def __iter__(self):
        self.signal_iter = iter(self.subcomponents[0])
        return self
    
    def __next__(self):
        (mix, props) = next(self.signal_iter)
        amp = props["amp"]
        
        # Add the delayed signal to the mix
        delayed_signal = self.delay_buffer[self.delay_buffer_index: self.delay_buffer_index + self.frames_per_chunk]
        if len(delayed_signal) < self.frames_per_chunk:
            delayed_signal = np.concatenate((delayed_signal, self.delay_buffer[0: self.frames_per_chunk - len(delayed_signal)]))
        delayed_signal *= self.wet_gain
        mix += delayed_signal

        # Add the current signal to the delay buffer
        if self.delay_buffer_index > self.delay_frames - self.frames_per_chunk:
            initial_chunk_size = self.delay_frames - self.delay_buffer_index
            leftover = self.frames_per_chunk - initial_chunk_size
            # self.log.debug(f"leftover: {leftover}")
            # self.log.debug(f"initial_chunk_size: {initial_chunk_size}")
            # self.log.debug(f"self.delay_buffer_index: {self.delay_buffer_index}")
            # self.log.debug(f"self.delay_buffer_index + initial_chunk_size: {self.delay_buffer_index + initial_chunk_size}")
            self.delay_buffer[self.delay_buffer_index: self.delay_buffer_index + initial_chunk_size] = mix[0: initial_chunk_size]
            self.delay_buffer[0: leftover] = mix[initial_chunk_size: initial_chunk_size + leftover]
        else:
            self.delay_buffer[self.delay_buffer_index: self.delay_buffer_index + self.frames_per_chunk] = mix
        
        # Update the delay buffer index
        self.delay_buffer_index = (self.delay_buffer_index + self.frames_per_chunk) % self.delay_frames

        # Update the amplitude
        self._props["amp"] = amp

        return (mix, self._props)


    
    def __deepcopy__(self, memo):
        return Delay(self.sample_rate, self.frames_per_chunk, subcomponents=[deepcopy(sub, memo) for sub in self.subcomponents], delay_time=self.delay_time)
    
    @property
    def delay_time(self):
        return self._delay_time

    @delay_time.setter
    def delay_time(self, value):
        self._delay_time = float(value)
        self.delay_frames = int(value * self.sample_rate)
        self.delay_buffer = np.zeros(self.delay_frames, np.float32)
        self.delay_buffer_index = 0