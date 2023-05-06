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
            period = 1 / self.frequency

            # Calculate the position within the sawtooth waveform based on chunk_start_time
            position_in_period = self._chunk_start_time % period

            # Generate a single cycle of the sawtooth wave, starting at the position_in_period
            ramp = np.linspace(-1, 1, int(self.sample_rate * period), endpoint=False)
            ramp_start_index = int(position_in_period * self.sample_rate)
            ramp = np.roll(ramp, -ramp_start_index)[:self.frames_per_chunk]
            ramp *= self.amplitude

            self._wave = np.tile(ramp, np.ceil(self.frames_per_chunk / len(ramp)).astype(int))[:self.frames_per_chunk]

        # Update the state variables for next time
        self._chunk_start_time = self._chunk_end_time
        self._chunk_end_time += self._chunk_duration

        return (self._wave.astype(np.float32), self._props)

    def __deepcopy__(self, memo):
        return SawtoothWaveOscillator(self.sample_rate, self.frames_per_chunk)
