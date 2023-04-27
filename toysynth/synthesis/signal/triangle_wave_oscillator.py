import logging
import numpy as np

from .oscillator import Oscillator

class TriangleWaveOscillator(Oscillator):
    def __init__(self, sample_rate, frames_per_chunk, name="TriWaveOscillator"):
        super().__init__(sample_rate, frames_per_chunk, name=name)
    
    def __iter__(self):
        self._wave = np.zeros(self.frames_per_chunk)
        self._chunk_duration = self.frames_per_chunk / self.sample_rate
        self._chunk_start_time = 0.0
        self._chunk_end_time = self._chunk_duration
        return self

    def __next__(self):
        if not self.active or self.frequency <= 0.0:
            if self.frequency < 0.0:
                self.log.error("Overriding negative frequency to 0")
            self._wave = np.zeros(self.frames_per_chunk, dtype=np.float32)
            self._props["amp"] = 0.0

        else:
            self._props["amp"] = 1.0
            p = 1/self.frequency #calculate the period for the formula
            ts = np.linspace(self._chunk_start_time, self._chunk_end_time, self.frames_per_chunk, endpoint=False)
            
            # Use NumPy vectorized operations to calculate the triangle wave
            self._wave = 4 * self.amplitude / p * np.abs(((ts - (p + 4 * self.phase) / 4) % p) - p / 2) - self.amplitude

            # Update the state variables for next time
            self._chunk_start_time = self._chunk_end_time
            self._chunk_end_time += self._chunk_duration

        # Return the wave array and properties outside the else block
        return (self._wave.astype(np.float32), self._props)

    def __deepcopy__(self, memo):
        return TriangleWaveOscillator(self.sample_rate, self.frames_per_chunk, name="TriWaveOscillator")