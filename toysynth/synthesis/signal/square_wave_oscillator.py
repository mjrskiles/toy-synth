import numpy as np

from .sin_wave_oscillator import SinWaveOscillator

class SquareWaveOscillator(SinWaveOscillator):
    def __init__(self, sample_rate, frames_per_chunk, default_frequency):
        super().__init__(sample_rate, frames_per_chunk, default_frequency)

    def __next__(self):
        sin_wave = super().__next__()
        square_wave = np.sign(sin_wave)
        # self.print_chunk(square_wave)
        return square_wave