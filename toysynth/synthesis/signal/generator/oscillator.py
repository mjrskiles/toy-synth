import logging
import numpy as np

from .generator import Generator

class Oscillator(Generator):
    def __init__(self, sample_rate, frames_per_buffer):
        super().__init__(sample_rate, frames_per_buffer)
        self.log = logging.getLogger(__name__)
        self._type = "Base"
        self.frequency = 440.0 # hertz
        self.phase = np.pi / 2.0
        self.amplitude = 1.0

    @property
    def type(self):
        """The Oscillator Type"""
        return self._type

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
            self.log.error(f"unable to set with value {value}")

    @property
    def phase(self):
        """The phase offset of the wave in radians"""
        return self._phase
    
    @phase.setter
    def phase(self, value):
        try:
            float_value = float(value)
            self._phase = float_value
        except:
            self.log.error(f"unable to set with value {value}")

    def set_phase_degrees(self, degrees):
        try:
            radians = (degrees / 360) * 2 * np.pi
            self.phase = radians
        except:
            self.log.error(f"[set_phase_degrees] unable to set with value {degrees}")

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
            self.log.error(f"unable to set with value {value}")
    
    def generate(self):
        self.log.error(f"Tried to use the oscillator base class!")