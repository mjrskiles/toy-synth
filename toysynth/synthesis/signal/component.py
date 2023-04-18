import logging

from .signal_type import SignalType

class Component():
    """
    Represents a base signal component. A signal component is an iterator.
    The iterator should return an ndarray of size <frames_per_chunk> with type numpy.float32
    A component can have subcomponents, which should also be iterators.
    """

    def __init__(self, sample_rate, frames_per_chunk, signal_type: SignalType) -> None:
        self.log = logging.getLogger(__name__)
        self.sample_rate = sample_rate
        self.frames_per_chunk = frames_per_chunk
        self.signal_type = signal_type

    def __iter__(self):
        return self
    
    def __next__(self):
        self.log.error("Child class should override the __next__ method")
        return
    
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