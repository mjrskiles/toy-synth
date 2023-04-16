import logging

from toysynth.synthesis.signal.component import Component

class Generator(Component):
    def __init__(self, sample_rate, frames_per_chunk):
        self.log = logging.getLogger(__name__)
        self.sample_rate = int(sample_rate)
        self.frames_per_chunk = int(frames_per_chunk)

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
            self.log.error(f"unable to set with value {value}")

    @property
    def frames_per_chunk(self):
        """The number of data frames to generate per call to generate. Essentially the size of the array to generate"""
        return self._frames_per_chunk
    
    @frames_per_chunk.setter
    def frames_per_chunk(self, value):
        try:
            int_value = int(value)
            self._frames_per_chunk = int_value
        except ValueError:
            self.log.error(f"unable to set with value {value}")