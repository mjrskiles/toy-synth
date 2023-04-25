import logging
from copy import deepcopy

import numpy as np

from .component import Component
from .oscillator import Oscillator
from .low_pass_filter import LowPassFilter
from .signal_type import SignalType

class Chain(Component):
    def __init__(self, sample_rate, frames_per_chunk, root_component):
        super().__init__(sample_rate, frames_per_chunk, signal_type=SignalType.WAVE)
        self.log = logging.getLogger(__name__)
        self.sample_rate = sample_rate
        self.frames_per_chunk = frames_per_chunk
        self.root_component = root_component

    def __iter__(self):
        self.root_iter = iter(self.root_component)
        return self
    
    def __next__(self):
        return next(self.root_iter)
    
    def __deepcopy__(self, memo):
        return Chain(self.sample_rate, self.frames_per_chunk, deepcopy(self.root_component))
    
    def get_components_by_class(self, cls):
        components = []

        def search_subcomponents(component):
            if isinstance(component, cls):
                components.append(component)
            if hasattr(component, "subcomponents") and len(component.subcomponents) > 0:
                for subcomponent in component.subcomponents:
                    search_subcomponents(subcomponent)

        search_subcomponents(self.root_component)
        return components
    
    def note_on(self, frequency):
        self.root_component.active = True
        for component in self.get_components_by_class(Oscillator):
            component.frequency = frequency

    def note_off(self):
        # Setting the root component active to False should propagate down the tree
        self.root_component.active = False

    def set_filter_cutoff(self, cutoff):
        for lpf in self.get_components_by_class(LowPassFilter):
            lpf.cutoff_frequency = np.float32(cutoff)