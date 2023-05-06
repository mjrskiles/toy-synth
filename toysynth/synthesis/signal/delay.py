import logging
from copy import deepcopy

import numpy as np

from .component import Component
from .signal_type import SignalType

class Delay(Component):
    def __init__(self, sample_rate, frames_per_chunk, subcomponents, name="Delay", delay_buffer_length=4.0) -> None:
        super().__init__(sample_rate, frames_per_chunk, signal_type=SignalType.WAVE, subcomponents=subcomponents, name=name)
        self.log = logging.getLogger(__name__)
        self.delay_buffer_length = delay_buffer_length
        self._delay_time = 0.1
        self.delay_frames = int(self.delay_buffer_length * self.sample_rate)
        self.delay_buffer = np.zeros(self.delay_frames, np.float32)
        self.delay_time_start_index = self.delay_frames - int(self.delay_time * self.sample_rate)
        self.log.debug(f"self.delay_time_start_index: {self.delay_time_start_index}")
        self.wet_gain = 0.5 

    def __iter__(self):
        self.signal_iter = iter(self.subcomponents[0])
        return self
    
    def __next__(self):
        (mix, props) = next(self.signal_iter)
        amp = props["amp"]
        
        # Add the delayed signal to the mix
        if self.delay_time > 0:
            delayed_signal = self.delay_buffer[self.delay_time_start_index: self.delay_time_start_index + self.frames_per_chunk]
            while len(delayed_signal) < self.frames_per_chunk:
                self.log.debug(f"Had to wrap around the delay buffer")
                delayed_signal = np.concatenate((delayed_signal, self.delay_buffer[self.delay_time_start_index: self.delay_time_start_index + self.frames_per_chunk - len(delayed_signal)]))
            
            delayed_signal *= self.wet_gain
            amp += self.wet_gain
            mix += delayed_signal

        # make sure the signal is between -1 and 1
        if amp > 1.0:
            # self.log.debug(f"Normalizing signal with amp {amp}")
            mix = mix / amp
            amp = 1.0

        # Add the current signal to the delay buffer
        self.delay_buffer = np.roll(self.delay_buffer, -self.frames_per_chunk)
        self.delay_buffer[self.delay_frames - self.frames_per_chunk: self.delay_frames] = mix

        # Update the amplitude
        self._props["amp"] = amp

        return (mix, self._props)


    
    def __deepcopy__(self, memo):
        return Delay(self.sample_rate, self.frames_per_chunk, subcomponents=[deepcopy(sub, memo) for sub in self.subcomponents], delay_buffer_length=self.delay_buffer_length)
    
    @property
    def delay_time(self):
        return self._delay_time

    @delay_time.setter
    def delay_time(self, value):
        self._delay_time = float(value)
        self.delay_time_start_index = self.delay_frames - int(self.delay_time * self.sample_rate)
