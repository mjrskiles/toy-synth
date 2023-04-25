import logging

from .component import Component
from .signal_type import SignalType

class Generator(Component):
    def __init__(self, sample_rate, frames_per_chunk, signal_type: SignalType):
        super().__init__(sample_rate, frames_per_chunk, signal_type, [])
        self.log = logging.getLogger(__name__)

    @property
    def active(self):
        """
        The active status. If a component is active it should do its job, otherwise act as a bypass.
        If the component is a generator it should generate zeros when inactive.
        """
        return self._active
    
    @active.setter
    def active(self, value):
        """
        Overrides the active setter in Component class
        """
        try:
            bool_val = bool(value)
            self._active = bool_val
        except ValueError:
            self.log.error(f"Unable to set with value {value}")