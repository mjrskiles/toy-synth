import logging

from toysynth.synthesis.signal.component import Component

class Generator(Component):
    def __init__(self, sample_rate, frames_per_chunk):
        super().__init__(sample_rate, frames_per_chunk)
        self.log = logging.getLogger(__name__)