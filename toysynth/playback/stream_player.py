import logging
import types

class StreamPlayer():
    def __init__(self, sample_rate, frames_per_buffer, input_delegate):
        self.log = logging.getLogger(__name__)
        self.sample_rate = sample_rate
        self.frames_per_buffer = frames_per_buffer
        self.input_delegate = input_delegate

    @property
    def sample_rate(self):
        return self._sample_rate
    
    @sample_rate.setter
    def sample_rate(self, value):
        try:
            if (int_value := int(value)) > 0:
                self._sample_rate = int_value
            else:
                raise ValueError
        except ValueError:
            self.log.error(f"Could set sample_rate with value {value}")

    @property
    def frames_per_buffer(self):
        return self._frames_per_buffer
    
    @frames_per_buffer.setter
    def frames_per_buffer(self, value):
        try:
            if (int_value := int(value)) > 0:
                self._frames_per_buffer = int_value
            else:
                raise ValueError
        except ValueError:
            self.log.error(f"Could set sample_rate with value {value}")

    @property
    def input_delegate(self):
        """
        This should be a callable object which returns the BYTES of an ndarray (aka calling tobytes() on it)
        of size <frames_per_buffer>
        """
        return self._input_delegate
    
    @input_delegate.setter
    def input_delegate(self, value):
        try:
            if isinstance(value, types.GeneratorType):
                self._input_delegate = value
            else:
                raise ValueError
        except ValueError:
            self.log.error(f"Could not set input delegate with value {value}")

    def play(self):
        self.log.error("Attempted to use base class")

    def stop(self):
        self.log.error("Attempted to use the base class")