import logging
import numpy as np

from .oscillator import Oscillator
from .utils import seconds_to_frames

class SawtoothWaveOscillator(Oscillator):
    def __init__(self, sample_rate, frames_per_chunk, name="SawtoothWaveOscillator"):
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
            self._wave = np.zeros(self.frames_per_chunk)
            self._props["amp"] = 0.0

        else:
            self._props["amp"] = self.amplitude
            ts = np.linspace(self._chunk_start_time, self._chunk_end_time, self.frames_per_chunk, endpoint=False)
            sawtooth_wave = self.amplitude * (2 * ((ts * self.frequency) % 1) - 1)
            self._wave = sawtooth_wave

        # Update the state variables for next time
        self._chunk_start_time = self._chunk_end_time
        self._chunk_end_time += self._chunk_duration

        return (self._wave.astype(np.float32), self._props)

    def __deepcopy__(self, memo):
        return SawtoothWaveOscillator(self.sample_rate, self.frames_per_chunk)
