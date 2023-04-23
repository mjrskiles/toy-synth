import logging
from copy import deepcopy

import numpy as np

from .component import Component
from .oscillator import Oscillator
from .low_pass_filter import LowPassFilter

class Chain(Component):
    def __init__(self, root_component):
        self.log = logging.getLogger(__name__)
        self.root_component = root_component

    def __iter__(self):
        self.root_iter = iter(self.root_component)
        return self
    
    def __next__(self):
        return next(self.root_iter)
    
    def __deepcopy__(self, memo):
        return Chain(deepcopy(self.root_component, memo))
    
    def get_components_by_class(self, cls):
        components = []

        def search_subcomponents(component):
            if isinstance(component, cls):
                components.append(component)
            if hasattr(component, "subcomponents"):
                for subcomponent in component.subcomponents:
                    search_subcomponents(subcomponent)

        search_subcomponents(self.root_component)
        return components
    
    def note_on(self, frequency):
        for component in self.get_components_by_class(Oscillator):
            component.frequency = frequency
            component.active = True

    def note_off(self):
        # Handle note off event in the signal chain, e.g., stop the oscillator(s)
        for component in self.get_components_by_class(Oscillator):
            component.active = False

    def set_filter_cutoff(self, cutoff):
        for lpf in self.get_components_by_class(LowPassFilter):
            lpf.cutoff_frequency = np.float32(cutoff)