import logging

class Oscillator:
    def __init__(self, sample_rate, sample_buffer_target_size):
        self.log = logging.getLogger(__name__)
        self._type = None
        self._sample_rate = sample_rate
        self._sample_buffer_target_size = sample_buffer_target_size
        self._frequency = 0.0 # hertz
        self._phase = 0.0
        self._amplitude = 1.0

    @property
    def type(self):
        """The Oscillator Type"""
        return self._type

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
    def sample_buffer_target_size(self):
        """The approximate size of the sample buffer."""
        return self._sample_buffer_target_size

    @sample_buffer_target_size.setter
    def sample_buffer_target_size(self, value):
        try:
            int_value = int(value)
            self._sample_buffer_target_size = int_value
        except ValueError:
            self.log.error(f"{__name__}: [sample_buffer_target_size] unable to set with value {value}")

    @property
    def frequency(self):
        """The wave frequency in hertz"""
        return self._frequency

    @frequency.setter
    def frequency(self, value):
        try:
            float_value = float(value)
            self._frequency = float_value
        except:
            self.log.error(f"{__name__}: [frequency] unable to set with value {value}")

    @property
    def phase(self):
        """The phase offset of the wave"""
        return self._phase
    
    @phase.setter
    def phase(self, value):
        try:
            float_value = float(value)
            self._phase = float_value
        except:
            self.log.error(f"{__name__}: [phase] unable to set with value {value}")

    @property
    def amplitude(self):
        """The wave amplitude from 0.0 to 1.0"""
        return self._amplitude

    @amplitude.setter
    def amplitude(self, value):
        try:
            float_value = float(value)
            if float_value >= 0.0 and float_value <= 1.0:
                self._amplitude = float_value
            else:
                raise ValueError
        except:
            self.log.error(f"{__name__}: [amplitude] unable to set with value {value}")
        
    def generate_sample(self):
        self.log.error(f"{__name__}: [generate_sample] Tried to use the oscillator base class!")
    