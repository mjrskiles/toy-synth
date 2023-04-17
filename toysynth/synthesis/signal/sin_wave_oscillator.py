import logging

import numpy as np

from .oscillator import Oscillator

class SinWaveOscillator(Oscillator):
    def __init__(self, sample_rate, frames_per_chunk, default_frequency):
        super().__init__(sample_rate, frames_per_chunk, default_frequency)

    def __iter__(self):
        self._wave = np.zeros(self.frames_per_chunk)
        self._chunk_duration = self.frames_per_chunk / self.sample_rate
        self._chunk_start_time = 0.0
        self._chunk_end_time = self._chunk_duration
        return self
    
    def __next__(self):
        # Generate the wave
        if self.frequency <= 0.0:
            if self.frequency < 0.0:
                self.log.error("Overriding negative frequency to 0")
            self._wave = np.zeros(self.frames_per_chunk)
        
        else:
            ts = np.linspace(self._chunk_start_time, self._chunk_end_time, self.frames_per_chunk, endpoint=False)
            # self.log.debug(f"phase: {self.phase}")
            self._wave = self.amplitude * np.sin(self.phase + (2 * np.pi * self.frequency) * ts)

        # self.log.debug(f"wave: {self._wave}")

        # Update the state variables for next time
        self._chunk_start_time = self._chunk_end_time
        self._chunk_end_time += self._chunk_duration

        return self._wave.astype(np.float32)

    def print_chunk(self, chunk):
        for frame in chunk:
            print("," + str(frame), end="")

            
