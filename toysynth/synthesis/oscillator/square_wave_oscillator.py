import logging

import numpy as np

import synthesis.oscillator.oscillator as osc

class SquareWaveOscillator(osc.Oscillator):
    def __init__(self, sample_rate, sample_buffer_target_size):
        super().__init__(sample_rate, sample_buffer_target_size)
        self._type = "Square"
        self.log = logging.getLogger(__name__)
        
    def generate_sample(self):
        if self.frequency <= 0.0:
            return np.zeros(self.sample_buffer_target_size).astype(np.float32)

        # Determine how many slices make up one cycle of the wave
        slices_per_cycle = int(self.sample_rate / self.frequency)
        # print(f"sample_rate = {self.sample_rate}")
        # print(f"frequency = {self.frequency}")
        # print(f"slices per cycle = {slices_per_cycle}")
        square_wave = np.hstack([np.ones(slices_per_cycle // 2) * self.amplitude, np.ones(slices_per_cycle // 2) * -self.amplitude])

        cycles_per_sample = self.sample_buffer_target_size // slices_per_cycle
        # print(f"Cycles per sample = {cycles_per_sample}")
        if cycles_per_sample <= 0:
            cycles_per_sample = 1
        square_wave = np.tile(square_wave, cycles_per_sample)
        # print(f"square_wave len = {len(square_wave)}")
        # np.set_printoptions(threshold=np.inf)
        # print(square_wave)
        return square_wave.astype(np.float32)