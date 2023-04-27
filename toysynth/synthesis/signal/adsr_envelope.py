import logging
from copy import deepcopy
from enum import Enum
import time

import numpy as np

from .component import Component
from .signal_type import SignalType

class AdsrEnvelope(Component):
    class State(Enum):
        IDLE = 0
        ADS = 1
        RELEASE = 2

    def __init__(self, sample_rate, frames_per_chunk, source: Component):
        super().__init__(sample_rate, frames_per_chunk, signal_type=SignalType.WAVE, subcomponents=[], name="ADSREnvelope")
        self.log = logging.getLogger(__name__)
        self.add_subcomponent(source)
        self._current_amplitude = 0.0
        self._attack = np.float32(0.2)
        self._decay = np.float32(0.3)
        self._sustain = np.float32(0.5)
        self._release = np.float32(0.5)
        self._iteration_number = 0
        self._sustain_frames_num = self.frames_per_chunk * 2
        self._target_amp = 1.0
        self.calculate_ads_ramps()
        self.calculate_r_ramp()
        self.state = AdsrEnvelope.State.IDLE

        # np.set_printoptions(threshold=self.sample_rate * 10)

    def __iter__(self):
        self.source_iter = iter(self.subcomponents[0])
        self._stage_trig_time = time.time()
        self._props["amp"] = self._current_amplitude
        return self
    
    def __next__(self):
        (source_chunk, props) = next(self.source_iter)
        if self._target_amp != props["amp"]:
            self._target_amp = props["amp"]
            self.calculate_ads_ramps()
        match self.state:
            case AdsrEnvelope.State.ADS:
                ramp_index = self._iteration_number * self.frames_per_chunk
                if ramp_index + self.frames_per_chunk > len(self._ads_ramp):
                    ramp_index = len(self._ads_ramp) - self.frames_per_chunk
                self._iteration_number += 1
                end_index = ramp_index + self.frames_per_chunk # ramp index is guaranteed to be within range
                ramp_chunk = self._ads_ramp[ramp_index:end_index]
                source_chunk = source_chunk * ramp_chunk
                # self.log.debug(f"Ramp chunk:\n{ramp_chunk}")
                self._current_amplitude = ramp_chunk[-1]

                now = time.time()
                elapsed = now - self._stage_trig_time
                if not self.active:
                    self.state = AdsrEnvelope.State.RELEASE
                    self._stage_trig_time = time.time()
                    self._iteration_number = 0
                    self.calculate_r_ramp()
                    self.log.debug(f"{self.name}: Triggered release state after {elapsed}s")

                self._props["amp"] = self._current_amplitude
                return (source_chunk, self._props)

            case AdsrEnvelope.State.RELEASE:
                now = time.time()
                elapsed = now - self._stage_trig_time
                ramp_index = self._iteration_number * self.frames_per_chunk
                self._iteration_number += 1
                if self.active:
                    self.trigger_attack()

                if ramp_index + self.frames_per_chunk > len(self._r_ramp):
                    partial_chunk = self._r_ramp[ramp_index:]
                    zeros = np.zeros((self.frames_per_chunk - len(partial_chunk)), dtype=np.float32)
                    ramp_chunk = np.concatenate([partial_chunk, zeros], axis=0)
                    self.log.debug(f"{self.name}: End of Release Ramp after {elapsed}s")
                    if not self.active:
                        self.state = AdsrEnvelope.State.IDLE
                else:
                    end_index = ramp_index + self.frames_per_chunk
                    ramp_chunk = self._r_ramp[ramp_index:end_index]
                source_chunk = source_chunk * ramp_chunk
                return (source_chunk, self._props)
            case AdsrEnvelope.State.IDLE:
                if self.active:
                    self.trigger_attack()
                self._props["amp"] = 0.0
                return (np.zeros(self.frames_per_chunk, dtype=np.float32), self._props)


        
    def __deepcopy__(self, memo):
        return AdsrEnvelope(self.sample_rate, self.frames_per_chunk, deepcopy(self.subcomponents[0], memo))
    
    @property
    def attack(self):
        return self._attack
    
    @attack.setter
    def attack(self, value):
        try:
            float_val = np.float32(value)
            self._attack = float_val
            self.calculate_ads_ramps()
        except ValueError:
            self.log.error(f"Couldn't set with value {value}")

    @property
    def decay(self):
        return self._decay

    @decay.setter
    def decay(self, value):
        try:
            float_val = np.float32(value)
            self._decay = float_val
            self.calculate_ads_ramps()
        except ValueError:
            self.log.error(f"Couldn't set with value {value}")

    @property
    def sustain(self):
        return self._sustain
    
    @sustain.setter
    def sustain(self, value):
        try:
            float_val = np.float32(value)
            self._sustain = float_val
            self.calculate_ads_ramps()
        except ValueError:
            self.log.error(f"Couldn't set with value {value}")

    @property
    def release(self):
        return self._release
    
    @release.setter
    def release(self, value):
        try:
            float_val = np.float32(value)
            self._release = float_val
        except ValueError:
            self.log.error(f"Couldn't set with value {value}")

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
        This setter overrides the Component setter and specifically does NOT deactivate its subcomponents automatically
        """
        try:
            bool_val = bool(value)
            self._active = bool_val
        except ValueError:
            self.log.error(f"Unable to set with value {value}")

    def calculate_ads_ramps(self):
        attack_frames = int(self.sample_rate * self.attack) # attack is in s
        attack_ramp = np.linspace(0, self._target_amp, attack_frames, dtype=np.float32, endpoint=False)

        decay_frames = int(self.sample_rate * self.decay)
        self._decay_index = attack_frames
        decay_ramp = np.linspace(self._target_amp, self.sustain, decay_frames, dtype=np.float32, endpoint=False)

        # we need to have at least one full chunk in the sustain ramp. 
        # Usually we'll partially cross into the sustain region from the decay in one chunk, 
        # then the next chunks can read from the sustain region over and over until the note is released
        sustain_frames = self._sustain_frames_num
        self._sustain_index = self._decay_index + decay_frames
        sustain_ramp = np.full(sustain_frames, self.sustain, dtype=np.float32)

        self._ads_ramp = np.concatenate([attack_ramp, decay_ramp, sustain_ramp], axis=0)
        # self.log.debug(f"ADS Ramp:\n{self._ads_ramp}")

    def calculate_r_ramp(self):
        release_frames = int(self.sample_rate * self.release)
        self._release_index = self._sustain_index + (self._sustain_frames_num)
        self._r_ramp = np.linspace(self._current_amplitude, 0, release_frames, endpoint=True)


    def trigger_attack(self):
        self.state = AdsrEnvelope.State.ADS
        self._stage_trig_time = time.time()
        self._iteration_number = 0
        for sub in self.subcomponents:
            sub.active = True
        self.log.info(f"{self.name}: Triggered attack stage")
