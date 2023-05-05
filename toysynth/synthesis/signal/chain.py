import logging
from copy import deepcopy

import numpy as np

from .component import Component
from .oscillator import Oscillator
from .low_pass_filter import LowPassFilter
from .adsr_envelope import AdsrEnvelope
from .signal_type import SignalType
from .delay import Delay

class Chain(Component):
    def __init__(self, sample_rate, frames_per_chunk, root_component: Component):
        super().__init__(sample_rate, frames_per_chunk, signal_type=SignalType.WAVE, subcomponents=[root_component], name="Chain")
        self.log = logging.getLogger(__name__)
        self.sample_rate = sample_rate
        self.frames_per_chunk = frames_per_chunk

    def __iter__(self):
        self.root_iter = iter(self.subcomponents[0])
        return self
    
    def __next__(self):
        (chunk, props) = next(self.root_iter)
        return (chunk, props)
    
    def __deepcopy__(self, memo):
        return Chain(self.sample_rate, self.frames_per_chunk, deepcopy(self.subcomponents[0], memo))
    
    def get_components_by_class(self, cls):
        components = []

        def search_subcomponents(component):
            if isinstance(component, cls):
                components.append(component)
            if hasattr(component, "subcomponents") and len(component.subcomponents) > 0:
                for subcomponent in component.subcomponents:
                    search_subcomponents(subcomponent)

        search_subcomponents(self.subcomponents[0])
        return components
    
    def note_on(self, frequency):
        self.active = True
        self.subcomponents[0].active = True
        for component in self.get_components_by_class(Oscillator):
            component.frequency = frequency

    def note_off(self):
        # Setting the root component active to False should propagate down the tree
        self.active = False
        self.subcomponents[0].active = False

    def set_filter_cutoff(self, cutoff):
        for lpf in self.get_components_by_class(LowPassFilter):
            lpf.cutoff_frequency = np.float32(cutoff)

    def set_attack(self, attack):
        for env in self.get_components_by_class(AdsrEnvelope):
            env.attack = attack

    def set_decay(self, decay):
        for env in self.get_components_by_class(AdsrEnvelope):
            env.decay = decay

    def set_sustain(self, sustain):
        for env in self.get_components_by_class(AdsrEnvelope):
            env.sustain = sustain

    def set_release(self, release):
        for env in self.get_components_by_class(AdsrEnvelope):
            env.release = release

    def set_delay_time(self, delay_time):
        for delay in self.get_components_by_class(Delay):
            delay.delay_time = delay_time

    def set_delay_wet_gain(self, wet_gain):
        for delay in self.get_components_by_class(Delay):
            delay.wet_gain = wet_gain

    def is_silent(self):
        return self.subcomponents[0].is_silent()
