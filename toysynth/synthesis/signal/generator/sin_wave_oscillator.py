import logging

import numpy as np

from .oscillator import Oscillator

class SinWaveOscillator(Oscillator):
    def __init__(self, sample_rate, frames_per_chunk):
        super().__init__(sample_rate, frames_per_chunk)

    def __iter__(self):
        self._wave = np.zeros(self.frames_per_chunk)
        self._chunk_duration = self.frames_per_chunk / self.sample_rate
        self._chunk_start_time = 0.0
        self._chunk_end_time = self._chunk_duration
        return self
    
    def __next__(self):
        if self.frequency <= 0.0:
            if self.frequency < 0.0:
                self.log.error("Overriding negative frequency to 0")
            self._wave = np.zeros(self.frames_per_chunk)
        
        else:
            ts = np.linspace(self._chunk_start_time, self._chunk_end_time, self.frames_per_chunk, endpoint=False)
            self._wave = np.sin(self.phase + (2 * np.pi * self.frequency) * ts)

        self._chunk_start_time = self._chunk_end_time
        self._chunk_end_time += self._chunk_duration
        return self._wave.astype(np.float32)

    def generator(self):
        wave = np.zeros(self.frames_per_chunk)
        # frame_duration = 1.0 / self.sample_rate
        chunk_duration = self.frames_per_chunk / self.sample_rate
        chunk_start_time = 0.0
        chunk_end_time = chunk_duration
        self.log.debug(f"chunk duration:\n{chunk_duration}")
        # print("frames", end="")
        while True:
            if self.frequency <= 0.0:
                if self.frequency < 0.0:
                    self.log.error("Overriding negative frequency to 0")
                wave = np.zeros(self.frames_per_chunk)
            
            else:
                # frames_per_cycle = int(self.sample_rate / self.frequency)
                ts = np.linspace(chunk_start_time, chunk_end_time, self.frames_per_chunk, endpoint=False)
                # self.log.debug(f"ts len: {len(ts)}")
                wave = np.sin(self.phase + (2 * np.pi * self.frequency) * ts)
            
            # self.print_chunk(wave)
            yield wave.astype(np.float32)

            chunk_start_time = chunk_end_time
            chunk_end_time += chunk_duration

    def print_chunk(self, chunk):
        for frame in chunk:
            print("," + str(frame), end="")

            
