import logging
import numpy as np

from .oscillator import Oscillator
from .sawtooth_wave_oscillator import SawtoothWaveOscillator

class TriangleWaveOscillator(SawtoothWaveOscillator):
    def __init__(self, sample_rate, frames_per_chunk, name="TriWaveOscillator"):
        super().__init__(sample_rate, frames_per_chunk, name=name)
    
    def __iter__(self):
        return super().__iter__()

    def __next__(self):
        (sawtooth, props) = super().__next__()
        triangle = (abs(sawtooth) - 0.5) * 2
        return (triangle, props)

    def __deepcopy__(self, memo):
        return TriangleWaveOscillator(self.sample_rate, self.frames_per_chunk, name="TriWaveOscillator")