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
        self.envelope_adr_vals = np.logspace(0, 1, 128, endpoint=True, base=10, dtype=np.float32) - 1 # range is from 0-9
        logspaced = np.logspace(0, 1, 128, endpoint=True, dtype=np.float32) # range is from 1-10
        self.envelope_s_vals = (logspaced - 1) / (10 - 1) # range is from 0-1
        self.delay_times = 0.5 * np.logspace(0, 2, 128, endpoint=True, base=2, dtype=np.float32) - 0.5 # range is from 0 - 6
        self.osc_mix_vals = np.linspace(0, 1, 128, endpoint=True, dtype=np.float32)
        self.stream_player = PyAudioStreamPlayer(sample_rate, frames_per_chunk, self.generator())
        self.mode = Synthesizer.Mode.POLY
        self.control_change_handler = self.cc_bank_a_handler
        self.set_gain_a(0.5)
        self.set_gain_b(0.5) # TODO should this be in setup signal chain?
        self.mono_stacks = [[] for _ in range(num_voices)]
        

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
                            # self.log.info(f"Note on {note_name} ({int_note}), chan {chan}")
                    case ["note_off", "-n", note, "-c", channel]:
                        int_note = int(note)
                        chan = int(channel)
                        note_name = midi.note_names[int(note)]
                        if chan < len(self.voices):
                            self.note_off(int_note, chan)
                            # self.log.info(f"Note off {note_name} ({int_note}), chan {chan}")
                    case ["control_change", "-c", channel, "-n", cc_num, "-v", control_val]:
                        self.control_change_handler(channel, cc_num, control_val)
                    case ["program_change", "-c", channel, "-n", program_num]:
                        self.log.info(f"Received PC : {message}")
                        if channel == "9" and program_num == "0":
                            if self.control_change_handler == self.cc_bank_a_handler:
                                self.control_change_handler = self.cc_bank_b_handler
                                self.log.info(f"Set control change handler to bank B")
                            else:
                                self.control_change_handler = self.cc_bank_a_handler
                                self.log.info(f"Set control change handler to bank A")
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
        osc_a = signal.SquareWaveOscillator(self.sample_rate, self.frames_per_chunk)
        osc_a_gain = signal.Gain(self.sample_rate, self.frames_per_chunk, signal.SignalType.WAVE, subcomponents=[osc_a], control_tag="gain_a")
        self.gain_a_ctrl_tag = osc_a_gain.control_tag

        osc_b = signal.SawtoothWaveOscillator(self.sample_rate, self.frames_per_chunk)
        # osc_b.set_phase_degrees(45)

        osc_b_gain = signal.Gain(self.sample_rate, self.frames_per_chunk, signal.SignalType.WAVE, subcomponents=[osc_b], control_tag="gain_b")
        self.gain_b_ctrl_tag = osc_b_gain.control_tag

        osc_mixer = signal.Mixer(self.sample_rate, self.frames_per_chunk, [osc_a_gain, osc_b_gain])

        adsr_env = signal.AdsrEnvelope(self.sample_rate, self.frames_per_chunk, osc_mixer)

        delay = signal.Delay(self.sample_rate, self.frames_per_chunk, [adsr_env], delay_buffer_length=4.0)

        lpf = signal.LowPassFilter(self.sample_rate, self.frames_per_chunk, delay, 8000.0)

        signal_chain = signal.Chain(self.sample_rate, self.frames_per_chunk, lpf)
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
        """
        Handle note on for mono mode
        Add the note to the mono stack and turn it on
        """
        note_id = self.get_note_id(note, chan)
        # self.log.debug(f"[mono] Setting voice {chan} note_on with note {note}, id {note_id}")
        self.mono_stacks[chan].append(note)
        freq = midi.frequencies[note]
        self.voices[chan].note_on(freq, note_id)
    
    def note_on_poly(self, note: int, chan: int):
        note_id = self.get_note_id(note, chan)
        freq = midi.frequencies[note]
        for i in range(len(self.voices)):
            voice = self.voices[i]
            if not voice.active:
                # self.log.debug(f"[poly] Setting voice {i} note_on with note {note}, id {note_id}")
                voice.note_on(freq, note_id)
                self.voices.append(self.voices.pop(i)) # Move this voice to the back of the list. It should be popped last
                break

            if i == len(self.voices) - 1:
                self.log.debug(f"Had no unused voices!")
                self.voices[0].note_off()
                self.voices[0].note_on(freq, note_id)
                self.voices.append(self.voices.pop(0))


    def note_on(self, note: int, chan: int):
        if self.mode == Synthesizer.Mode.MONO:
            self.note_on_mono(note, chan)
        else:
            self.note_on_poly(note, chan)

    def note_off(self, note: int, chan: int):
        if self.mode == Synthesizer.Mode.MONO:
            self.note_off_mono(note, chan)
        else:
            self.note_off_poly(note, chan)

    def note_off_mono(self, note: int, chan: int):
        """
        Handle note off for mono mode
        If the note that is being turned off is the same as the note that is currently playing
        then turn it off and pop the note from the mono stack, then turn on the last note in the stack.
        Otherwise, just remove the note from the mono stack.
        """
        note_id = self.get_note_id(note, chan)
        if self.voices[chan].id == note_id:
            popped = self.mono_stacks[chan].pop()
            if popped != note:
                self.log.debug(f"Note {note} was not the same as the note that was popped {popped}")
            self.voices[chan].note_off()
            if len(self.mono_stacks[chan]) > 0:
                last_note = self.mono_stacks[chan].pop()
                self.note_on_mono(last_note, chan)
        else:
            try:
                self.mono_stacks[chan].remove(note)
            except ValueError:
                self.log.debug(f"Couldn't remove note {note} from mono stack")


    def note_off_poly(self, note: int, chan: int):
        note_id = self.get_note_id(note, chan)
        for i in range(len(self.voices)):
            voice = self.voices[i]
            if voice.active and voice.id == note_id:
                # self.log.debug(f"Setting voice {i} note_off with id {note_id}")
                voice.note_off()
    
    def all_notes_off(self):
        for voice in self.voices:
            voice.note_off()

    def set_attack(self, attack):
        for voice in self.voices:
            voice.signal_chain.set_attack(attack)

    def set_decay(self, decay):
        for voice in self.voices:
            voice.signal_chain.set_decay(decay)

    def set_sustain(self, sustain):
        for voice in self.voices:
            voice.signal_chain.set_sustain(sustain)

    def set_release(self, release):
        for voice in self.voices:
            voice.signal_chain.set_release(release)
    
    def set_cutoff_frequency(self, cutoff):
        for voice in self.voices:
            voice.signal_chain.set_filter_cutoff(cutoff)

    def set_delay_time(self, delay_time):
        for voice in self.voices:
            voice.signal_chain.set_delay_time(delay_time)

    def set_delay_wet_gain(self, wet_gain):
        for voice in self.voices:
            voice.signal_chain.set_delay_wet_gain(wet_gain)

    def set_gain_a(self, gain):
        for voice in self.voices:
            voice.signal_chain.set_gain_by_control_tag(self.gain_a_ctrl_tag, gain)

    def set_gain_b(self, gain):
        for voice in self.voices:
            voice.signal_chain.set_gain_by_control_tag(self.gain_b_ctrl_tag, gain)

    def cc_bank_a_handler(self, channel, cc_num, control_val):
        if cc_num == "20":
            cc_val = int(control_val)
            if cc_val != 0 and self.mode == Synthesizer.Mode.MONO:
                self.mode = Synthesizer.Mode.POLY
                self.log.info(f"Set synth mode to POLY")
            elif cc_val != 0:
                self.mode = Synthesizer.Mode.MONO
                self.log.info(f"Set synth mode to MONO")
        elif cc_num == "21":
            cc_val = int(control_val)
            if cc_val != 0:
                self.all_notes_off()
                self.log.info(f"Turned off all notes")
        elif cc_num == "70":
            cc_val = int(control_val)
            lookup_val = self.envelope_adr_vals[cc_val]
            self.set_attack(lookup_val)
            self.log.info(f"Attack: {lookup_val}")
        elif cc_num == "71":
            cc_val = int(control_val)
            lookup_val = self.envelope_adr_vals[cc_val]
            self.set_decay(lookup_val)
            self.log.info(f"Decay: {lookup_val}")
        elif cc_num == "72":
            cc_val = int(control_val)
            lookup_val = self.envelope_s_vals[cc_val]
            self.set_sustain(lookup_val)
            self.log.info(f"Sustain: {lookup_val}")
        elif cc_num == "73":
            cc_val = int(control_val)
            lookup_val = self.envelope_adr_vals[cc_val]
            self.set_release(lookup_val)
            self.log.info(f"Release: {lookup_val}")
        elif cc_num == "74":
            chan = int(channel)
            cc_val = int(control_val)
            self.set_cutoff_frequency(self.cutoff_vals[cc_val])
            self.log.info(f"LPF Cutoff: {self.cutoff_vals[cc_val]}")
        elif cc_num == "75":
            cc_val = int(control_val)
            gain_a_mix_val = self.osc_mix_vals[cc_val]
            gain_b_mix_val = 1 - gain_a_mix_val
            self.set_gain_a(gain_a_mix_val)
            self.set_gain_b(gain_b_mix_val)
            self.log.info(f"Gain A: {gain_a_mix_val}")
            self.log.info(f"Gain B: {gain_b_mix_val}")
        elif cc_num == "76":
            chan = int(channel)
            cc_val = int(control_val)
            self.set_delay_time(self.delay_times[cc_val])
            self.log.info(f"Delay Time: {self.delay_times[cc_val]}")
        elif cc_num == "77":
            chan = int(channel)
            cc_val = int(control_val)
            self.set_delay_wet_gain(self.envelope_s_vals[cc_val]) # range is 0 - 1
            self.log.info(f"Delay Wet Gain: {self.envelope_s_vals[cc_val]}")
        elif cc_num == "126":
            self.mode = Synthesizer.Mode.MONO
            self.log.info(f"Set synth mode to MONO")
        elif cc_num == "127":
            self.mode = Synthesizer.Mode.POLY
            self.log.info(f"Set synth mode to POLY")
        else:
            self.log.info(f"Unhandled control change: CC {cc_num} with value {control_val} on channel {channel}")

    def cc_bank_b_handler(self, channel, cc_num, control_val):
        self.log.info(f"Unhandled control change: CC {cc_num} with value {control_val} on channel {channel}")


class Voice:
    def __init__(self, signal_chain: signal.Chain):
        self.signal_chain = iter(signal_chain)
        self._active = False
        self.id = None

    @property
    def active(self):
        # Update the active status based on the is_silent() method of the ADSR envelope
        # Yeah it's kinda janks but it works. 
        if self._active and self.signal_chain.is_silent():
            self._active = False
        return self._active

    def note_on(self, frequency, id):
        self._active = True
        self.id = id
        self.signal_chain.note_on(frequency)

    def note_off(self):
        self.signal_chain.note_off()
