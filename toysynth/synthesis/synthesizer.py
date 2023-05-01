import logging
import threading
from copy import deepcopy
import hashlib
from enum import Enum

import numpy as np

from toysynth.communication import Mailbox
import toysynth.synthesis.signal as signal
import toysynth.midi as midi
from toysynth.playback import PyAudioStreamPlayer
import toysynth.synthesis.signal.utils as utils

class Synthesizer(threading.Thread):
    class Mode(Enum):
        MONO = 0
        POLY = 1

    def __init__(self, mailbox: Mailbox, sample_rate: int, frames_per_chunk: int, num_voices=8) -> None:
        super().__init__(name="Synthesizer")
        self.log = logging.getLogger(__name__)
        self.mailbox = mailbox
        self.sample_rate = sample_rate
        self.frames_per_chunk = frames_per_chunk
        self.signal_chain_prototype = self.setup_signal_chain()
        self.log.info(f"Signal Chain Prototype:\n{str(self.signal_chain_prototype)}")
        self.voices = [Voice(deepcopy(self.signal_chain_prototype)) for _ in range(num_voices)]
        self.cutoff_vals = np.logspace(4, 14, 128, endpoint=True, base=2, dtype=np.float32) # 2^14=16384 : that is the highest possible cutoff value
        self.stream_player = PyAudioStreamPlayer(sample_rate, frames_per_chunk, self.generator())
        self.mode = Synthesizer.Mode.POLY


    def run(self):
        self.stream_player.play()
        should_run = True
        while should_run and self.stream_player.is_active():
            # get() is a blocking call
            if message := self.mailbox.get(): 
                match message.split():
                    case ["exit"]:
                        self.log.info("Got exit command.")
                        self.stream_player.stop()
                        should_run = False
                    case ["note_on", "-n", note, "-c", channel]:
                        int_note = int(note)
                        chan = int(channel)
                        note_name = midi.note_names[int_note]
                        if chan < len(self.voices):
                            self.note_on(int_note, chan)
                            self.log.info(f"Note on {note_name} ({int_note}), chan {chan}")
                    case ["note_off", "-n", note, "-c", channel]:
                        int_note = int(note)
                        chan = int(channel)
                        note_name = midi.note_names[int(note)]
                        if chan < len(self.voices):
                            self.note_off(int_note, chan)
                            self.log.info(f"Note off {note_name} ({int_note}), chan {chan}")
                    case ["control_change", "-c", channel, "-n", cc_num, "-v", control_val]:
                        if cc_num == "74":
                            chan = int(channel)
                            # cc_num = int(control_num)
                            cc_val = int(control_val)
                            self.set_cutoff_frequency(self.cutoff_vals[cc_val])
                            self.log.info(f"LPF Cutoff: {self.cutoff_vals[cc_val]}")

                        elif cc_num == "126":
                            self.mode = Synthesizer.Mode.MONO
                            self.log.info(f"Set synth mode to MONO")
                        elif cc_num == "127":
                            self.mode = Synthesizer.Mode.POLY
                            self.log.info(f"Set synth mode to POLY")
                    case _:
                        self.log.info(f"Matched unknown command: {message}")
        return
    
    @property
    def mode(self):
        """Mono/Poly mode"""
        return self._mode
    
    @mode.setter
    def mode(self, val):
        try:
            if isinstance(val, Synthesizer.Mode):
                self._mode = val
            else:
                raise ValueError
        except ValueError:
            self.log.debug(f"Couldn't set Synthesizer mode with value {val}")

    def setup_signal_chain(self):
        osc_a = signal.SawtoothWaveOscillator(self.sample_rate, self.frames_per_chunk)
        osc_b = signal.TriangleWaveOscillator(self.sample_rate, self.frames_per_chunk)
        # osc_b.set_phase_degrees(45)

        osc_mixer = signal.Mixer(self.sample_rate, self.frames_per_chunk, [osc_a, osc_b])

        lpf = signal.LowPassFilter(self.sample_rate, self.frames_per_chunk, osc_mixer, 8000.0)

        adsr_env = signal.AdsrEnvelope(self.sample_rate, self.frames_per_chunk, lpf)

        signal_chain = signal.Chain(self.sample_rate, self.frames_per_chunk, adsr_env)
        return iter(signal_chain)
    
    def generator(self):
        mix = np.zeros(self.frames_per_chunk, np.float32)
        num_active_voices = 0
        while True:
            amp = np.float32(0.0)
            for i in range(len(self.voices)):
                voice = self.voices[i]
                (next_chunk, props) = next(voice.signal_chain)
                mix += next_chunk
                chunk_amp = props["amp"]
                amp += chunk_amp
                if chunk_amp != 0: # if the chunk isn't all 0s that means it's active
                    # self.log.debug(f"Voice {i} is active")
                    num_active_voices += 1

            # if num_active_voices != 0:
            #     mix = mix / num_active_voices
            # self.log.debug(f"amp: {amp}")
            if amp > 1:
                utils.normalize(mix)
            
            mix.clip(-1.0, 1.0)
            
            yield mix
            mix = np.zeros(self.frames_per_chunk, np.float32)
            num_active_voices = 0

    def get_note_id(self, note: int, chan: int):
        """
        Generate an id for a given note and channel
        By hashing the note and channel we can ensure that we are turning off the exact note
        that was turned on
        """
        note_id = hash(f"{note}{chan}")
        return note_id
    
    def note_on_mono(self, note: int, chan: int):
        note_id = self.get_note_id(note, chan)
        self.log.debug(f"[mono] Setting voice {chan} note_on with note {note}, id {note_id}")
        freq = midi.frequencies[note]
        self.voices[chan].note_on(freq, note_id)
    
    def note_on_poly(self, note: int, chan: int):
        note_id = self.get_note_id(note, chan)
        for i in range(len(self.voices)):
            voice = self.voices[i]
            if not voice.active:
                self.log.debug(f"[poly] Setting voice {i} note_on with note {note}, id {note_id}")
                freq = midi.frequencies[note]
                voice.note_on(freq, note_id)
                break

    def note_on(self, note: int, chan: int):
        if self.mode == Synthesizer.Mode.MONO:
            self.note_on_mono(note, chan)
        else:
            self.note_on_poly(note, chan)


    def note_off(self, note: int, chan: int):
        note_id = self.get_note_id(note, chan)
        for i in range(len(self.voices)):
            voice = self.voices[i]
            if voice.active and voice.id == note_id:
                self.log.debug(f"Setting voice {i} note_off with id {note_id}")
                voice.note_off()

    def set_cutoff_frequency(self, cutoff):
        for voice in self.voices:
            voice.signal_chain.set_filter_cutoff(cutoff)


class Voice:
    def __init__(self, signal_chain: signal.Chain):
        self.signal_chain = iter(signal_chain)
        self._active = False
        self.id = None

    @property
    def active(self):
        # Update the active status based on the is_silent() method of the ADSR envelope
        if self._active and self.signal_chain.is_silent():
            self._active = False
        return self._active

    def note_on(self, frequency, id):
        self._active = True
        self.id = id
        self.signal_chain.note_on(frequency)

    def note_off(self):
        self.signal_chain.note_off()
