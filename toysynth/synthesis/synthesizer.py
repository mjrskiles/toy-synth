import logging
import threading
from copy import deepcopy
import hashlib

import numpy as np

from toysynth.communication import Mailbox
import toysynth.synthesis.signal as signal
import toysynth.midi as midi
from toysynth.playback import PyAudioStreamPlayer
import toysynth.synthesis.signal.utils as utils

class Synthesizer(threading.Thread):
    def __init__(self, mailbox: Mailbox, sample_rate: int, frames_per_chunk: int, num_voices=8) -> None:
        super().__init__(name="Synthesizer")
        self.log = logging.getLogger(__name__)
        self.mailbox = mailbox
        self.sample_rate = sample_rate
        self.frames_per_chunk = frames_per_chunk

        self.signal_chain_prototype = self.setup_signal_chain()
        self.voices = [Voice(deepcopy(self.signal_chain_prototype)) for _ in range(num_voices)]

        self.stream_player = PyAudioStreamPlayer(sample_rate, frames_per_chunk, self.generator())


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
                        note_id = self.get_note_id(int_note, chan)
                        self.note_on(int_note, note_id)
                        self.log.info(f"Note on {note_name} ({int_note}), chan {chan}")
                    case ["note_off", "-n", note, "-c", channel]:
                        int_note = int(note)
                        chan = int(channel)
                        note_name = midi.note_names[int(note)]
                        note_id = self.get_note_id(int_note, chan)
                        self.note_off(note_id)
                        self.log.info(f"Note off {note_name} ({int_note}), chan {chan}")
                    case ["control_change", "-c", channel, "-n", "74", "-v", control_val]:
                        chan = int(channel)
                        # cc_num = int(control_num)
                        cc_val = int(control_val)
                        cutoff_vals = np.logspace(4, 14, 128, endpoint=True, base=2, dtype=np.float32) # 2^14=16384 : that is the highest possible cutoff value
                        self.set_cutoff_frequency(cutoff_vals[cc_val])
                        self.log.info(f"LPF Cutoff: {cutoff_vals[cc_val]}")
                    case _:
                        self.log.info(f"Matched unknown command: {message}")
        return

    def setup_signal_chain(self):
        osc_a = signal.SinWaveOscillator(self.sample_rate, self.frames_per_chunk)
        osc_b = signal.TriangleWaveOscillator(self.sample_rate, self.frames_per_chunk)
        # osc_b.set_phase_degrees(45)

        osc_mixer = signal.Mixer(self.sample_rate, self.frames_per_chunk, [osc_a])

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

    def note_on(self, note: int, id):
        for voice in self.voices:
            if not voice.active:
                freq = midi.frequencies[note]
                voice.note_on(freq, id)
                break

    def note_off(self, id):
        for voice in self.voices:
            if voice.active and voice.id == id:
                voice.note_off()

    def set_cutoff_frequency(self, cutoff):
        for voice in self.voices:
            voice.signal_chain.set_filter_cutoff(cutoff)


class Voice:
    def __init__(self, signal_chain: signal.Chain):
        self.signal_chain = iter(signal_chain)
        self.active = False
        self.id = None

    def note_on(self, frequency, id):
        if not self.active:
            self.active = True
            self.id = id
            self.signal_chain.note_on(frequency)

    def note_off(self):
        self.active = False
        self.signal_chain.note_off()