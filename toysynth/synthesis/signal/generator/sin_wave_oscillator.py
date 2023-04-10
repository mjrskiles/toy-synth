import logging

import numpy as np

import synthesis.signal.generator.oscillator as oscillator

class SinWaveOscillator(oscillator.Oscillator):
    def __init__(self, sample_rate, frames_per_buffer):
        super().__init__(sample_rate, frames_per_buffer)

    def generate(self):
        wave = np.zeros(self.frames_per_buffer)
        duration = self.frames_per_buffer / self.sample_rate
        self.log.debug(f"duration:\n{duration}")
        running_angle = 2 * np.pi # radians
        while True:
            if self.frequency <= 0.0:
                wave = np.zeros(self.frames_per_buffer)
                self.log.debug(f"1 wave:\n{wave}")
            else:
                # Determine how many slices make up one cycle of the wave
                slices_per_cycle = int(self.sample_rate / self.frequency)
                ts = np.linspace(0, duration, self.frames_per_buffer)
                # self.log.debug(f"ts:\n{ts}")
                wave = np.sin(2 * np.pi * self.frequency * ts) # TODO add phase
                running_angle += (self.frames_per_buffer / slices_per_cycle) * 2 * np.pi
                self.log.debug(f"2 wave:\n{wave}")

            yield wave.astype(np.float32)



            
