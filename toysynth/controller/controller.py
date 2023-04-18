import logging
import threading
from time import sleep

import toysynth.synthesis.signal as signal
from toysynth.playback.pyaudio_stream_player import PyAudioStreamPlayer
from toysynth.communication import Mailbox
import toysynth.midi as midi

class Controller(threading.Thread):
    def __init__(self, mailbox: Mailbox, sample_rate, frames_per_chunk):
        super().__init__()
        self.log = logging.getLogger(__name__)
        self.mailbox = mailbox

        ### BEGIN TEMPORARY SPAGHETTI CODE ###
        #  Temp components
        self.osc_a = signal.SquareWaveOscillator(sample_rate, frames_per_chunk, default_frequency=0.0)
        self.osc_b = signal.SquareWaveOscillator(sample_rate, frames_per_chunk, default_frequency=0.0)
        self.osc_b.set_phase_degrees(45)
        self.amp_osc_a = signal.ConstantValueGenerator(sample_rate, frames_per_chunk)
        self.amp_osc_b = signal.ConstantValueGenerator(sample_rate, frames_per_chunk)
        # self.amp_osc_b = signal.SinWaveOscillator(sample_rate, frames_per_chunk, default_frequency=0.5)
        self.ab_mixer = signal.DualMixer(sample_rate, frames_per_chunk, self.osc_a, self.osc_b, self.amp_osc_a, self.amp_osc_b)
        # self.noise_gen = signal.NoiseGenerator(sample_rate, frames_per_chunk)

        self.osc_c = signal.SquareWaveOscillator(sample_rate, frames_per_chunk, default_frequency=0.0)
        self.osc_c.set_phase_degrees(90)
        self.osc_d = signal.SquareWaveOscillator(sample_rate, frames_per_chunk, default_frequency=0.0)
        self.osc_d.set_phase_degrees(135)
        self.amp_osc_c = signal.ConstantValueGenerator(sample_rate, frames_per_chunk)
        self.amp_osc_d = signal.ConstantValueGenerator(sample_rate, frames_per_chunk)

        self.cd_mixer = signal.DualMixer(sample_rate, frames_per_chunk, self.osc_c, self.osc_d, self.amp_osc_c, self.amp_osc_d)

        self.amp_ab_mixer = signal.ConstantValueGenerator(sample_rate, frames_per_chunk)
        self.amp_cd_mixer = signal.ConstantValueGenerator(sample_rate, frames_per_chunk)
        self.abcd_mixer = signal.DualMixer(sample_rate, frames_per_chunk, self.ab_mixer, self.cd_mixer, self.amp_ab_mixer, self.amp_cd_mixer)

        self.osc_e = signal.SquareWaveOscillator(sample_rate, frames_per_chunk, default_frequency=0.0)
        self.osc_f = signal.SquareWaveOscillator(sample_rate, frames_per_chunk, default_frequency=0.0)
        self.osc_f.set_phase_degrees(45)
        self.amp_osc_e = signal.ConstantValueGenerator(sample_rate, frames_per_chunk)
        self.amp_osc_f = signal.ConstantValueGenerator(sample_rate, frames_per_chunk)
        # self.amp_osc_b = signal.SinWaveOscillator(sample_rate, frames_per_chunk, default_frequency=0.5)
        self.ef_mixer = signal.DualMixer(sample_rate, frames_per_chunk, self.osc_e, self.osc_f, self.amp_osc_e, self.amp_osc_f)
        # self.noise_gen = signal.NoiseGenerator(sample_rate, frames_per_chunk)

        self.osc_g = signal.SquareWaveOscillator(sample_rate, frames_per_chunk, default_frequency=0.0)
        self.osc_g.set_phase_degrees(90)
        self.osc_h = signal.SquareWaveOscillator(sample_rate, frames_per_chunk, default_frequency=0.0)
        self.osc_h.set_phase_degrees(135)
        self.amp_osc_g = signal.ConstantValueGenerator(sample_rate, frames_per_chunk)
        self.amp_osc_h = signal.ConstantValueGenerator(sample_rate, frames_per_chunk)

        self.gh_mixer = signal.DualMixer(sample_rate, frames_per_chunk, self.osc_g, self.osc_h, self.amp_osc_g, self.amp_osc_h)

        self.amp_ef_mixer = signal.ConstantValueGenerator(sample_rate, frames_per_chunk)
        self.amp_gh_mixer = signal.ConstantValueGenerator(sample_rate, frames_per_chunk)
        self.efgh_mixer = signal.DualMixer(sample_rate, frames_per_chunk, self.ef_mixer, self.gh_mixer, self.amp_ef_mixer, self.amp_gh_mixer)

        # abcdefgh mixer
        self.amp_abcd_mixer = signal.ConstantValueGenerator(sample_rate, frames_per_chunk)
        self.amp_efgh_mixer = signal.ConstantValueGenerator(sample_rate, frames_per_chunk)
        self.abcdefgh_mixer = signal.DualMixer(sample_rate, frames_per_chunk, self.abcd_mixer, self.efgh_mixer, self.amp_abcd_mixer, self.amp_efgh_mixer)

        self.signal_root = self.abcdefgh_mixer

        self.oscillators = [self.osc_a, self.osc_b, self.osc_c, self.osc_d, self.osc_e, self.osc_f, self.osc_g, self.osc_h]

        ### END TEMPORARY SPAGHETTI CODE ###

        self.stream_player = PyAudioStreamPlayer(sample_rate, frames_per_chunk, iter(self.signal_root))

    def run(self):
        self.stream_player.play()
        should_run = True
        freqs = [osc.frequency for osc in self.oscillators]
        while should_run and self.stream_player.is_active():
            # get() is a blocking call
            if message := self.mailbox.get(): 
                match message.split():
                    case ["exit"]:
                        self.log.debug("Got exit command.")
                        self.stream_player.stop()
                        should_run = False
                    case ["note_on", "-f", freq]:
                        self.osc_a.frequency = freq
                        self.osc_b.frequency = freq
                    case ["note_on", "-n", note, "-c", channel]:
                        freq = midi.frequencies[int(note)]
                        chan = int(channel)
                        note_name = midi.note_names[int(note)]
                        self.log.info(f"Note on {note_name} ({freq}), chan {chan}")
                        if chan >= len(self.oscillators):
                            self.log.info(f"Received message for non-existent voice {chan}")
                        else:
                            freqs[chan] = freq
                        # self.log.debug(f"Adding frequency: {freq}")
                        for i in range(len(self.oscillators)):
                            self.oscillators[i].frequency = freqs[i]
                    case ["note_off", "-n", note, "-c", channel]:
                        # self.log.debug(f"Got note off command: {message}")
                        freq = midi.frequencies[int(note)]
                        chan = int(channel)
                        note_name = midi.note_names[int(note)]
                        self.log.info(f"Note off {note_name} ({freq}), chan {chan}")
                        if chan >= 0 and chan < len(self.oscillators):
                            freqs[chan] = 0.0 
                        for i in range(len(self.oscillators)):
                            self.oscillators[i].frequency = freqs[i]
                    case _:
                        self.log.info(f"Matched unknown command: {message}")
        return

    

        