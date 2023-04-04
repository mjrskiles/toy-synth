import numpy as np

import synth.oscillator.oscillator as osc

class SquareWaveOscillator(osc.Oscillator):
    def __init__(self, sample_rate):
        super().__init__()
        self._type = "Square"
        self._sample_rate = 44100 # hertz
        self._cycles_per_sample = 10 # The number of times to repeat the sample in the buffer
        self._frequency = 440.0 # hertz
        self._amplitude = 0.05
        self.buffer = np.zeros(1) # initialize an empty buffer
    
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
    def cycles_per_sample(self):
        """
        The number of times to repeat the sample in the buffer
        This should limit the CPU usage by preventing the pyaudio callback from 
        being triggered once per wave cycle
        """
        return self._cycles_per_sample

    @cycles_per_sample.setter
    def cycles_per_sample(self, value):
        try:
            float_value = float(value)
            self._cycles_per_sample = float_value
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
        slices_per_cycle = int(self.sample_rate / self.frequency)
        square_wave = np.hstack([np.ones(slices_per_cycle // 2) * self.amplitude, np.ones(slices_per_cycle // 2) * -self.amplitude])
        square_wave = np.tile(square_wave, self.cycles_per_sample)
        return square_wave.astype(np.float32)