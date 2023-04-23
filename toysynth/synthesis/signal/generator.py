import logging

from .component import Component
from .signal_type import SignalType

class Generator(Component):
    def __init__(self, sample_rate, frames_per_chunk, signal_type: SignalType):
        super().__init__(sample_rate, frames_per_chunk, signal_type)
        self.log = logging.getLogger(__name__)