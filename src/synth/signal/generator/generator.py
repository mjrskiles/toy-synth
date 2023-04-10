import logging

import synth.signal.component as component

class Generator(component.Component):
    def __init__(self, sample_rate, frames_per_buffer):
        self.log = logging.getLogger(__name__)
        self.sample_rate = int(sample_rate)
        self.frames_per_buffer = int(frames_per_buffer)

    @property
    def sample_rate(self):
        """The number of sample slices per second"""
        return self._sample_rate

    @sample_rate.setter
    def sample_rate(self, value):
        try:
            int_value = int(value)
            self._sample_rate = int_value
        except ValueError:
            self.log.error(f"{__name__}: [sample_rate] unable to set with value {value}")

    @property
    def frames_per_buffer(self):
        """The number of data frames to generate per call to generate. Essentially the size of the array to generate"""
        return self._frames_per_buffer
    
    @frames_per_buffer.setter
    def frames_per_buffer(self, value):
        try:
            int_value = int(value)
            self._frames_per_buffer = int_value
        except ValueError:
            self.log.error(f"{__name__}: [frames_per_buffer] unable to set with value {value}")

    def generate(self):
        self.log.error(f"{__name__}: [generate] Tried to use the generator base class!")