import logging

import numpy as np

from .oscillator import Oscillator

class SinWaveOscillator(Oscillator):
    def __init__(self, sample_rate, frames_per_buffer):
        super().__init__(sample_rate, frames_per_buffer)

    def generator(self):
        wave = np.zeros(self.frames_per_buffer)
        duration = self.frames_per_buffer / self.sample_rate
        chunk_start_time = 0.0
        chunk_end_time = duration
        self.log.debug(f"duration:\n{duration}")

        while True:
            if self.frequency <= 0.0:
                if self.frequency < 0.0:
                    self.log.error("Overriding negative frequency to 0")
                wave = np.zeros(self.frames_per_buffer)
            
            else:
                # frames_per_cycle = int(self.sample_rate / self.frequency)
                ts = np.linspace(chunk_start_time, chunk_end_time, self.frames_per_buffer)
                wave = np.sin(2 * np.pi * self.frequency * ts) # TODO add phase offset
            
            # self.log.debug(f"wave:\n{wave}")
            yield wave.astype(np.float32)

            chunk_start_time = chunk_end_time
            chunk_end_time += duration



            
