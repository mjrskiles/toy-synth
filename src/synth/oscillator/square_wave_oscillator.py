import numpy as np

import synth.oscillator.oscillator as osc

class SquareWaveOscillator(osc.Oscillator):
    def __init__(self, sample_rate):
        super().__init__()
        self._type = "Square"
        self._sample_rate = 44100 # hertz
        self._duration = 1.0 # seconds
        self._frequency = 440.0 # hertz
        self._amplitude = 1.0
        self.buffer_length = int(self._sample_rate * self._duration)
        self.buffer = np.zeros(self.buffer_length) # initialize an empty buffer
    
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
            print(f"{__name__}: [sample_rate] unable to set with value {value}")

    @property
    def duration(self):
        """The length in seconds of the sample to be generated"""
        return self._duration

    @duration.setter
    def duration(self, value):
        try:
            float_value = float(value)
            self._duration = float_value
        except:
            print(f"{__name__}: [duration] unable to set with value {value}")

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
            print(f"{__name__}: [frequency] unable to set with value {value}")

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
            print(f"{__name__}: [amplitude] unable to set with value {value}")
        
    def generate_sample(self):
        t = np.linspace(0, self.duration, self.buffer_length, endpoint=False)
        square_wave = np.sign(np.sin(2 * np.pi * self.frequency * t)) * self.amplitude
        return square_wave.astype(np.float32)
    