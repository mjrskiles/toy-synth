import logging
import threading
from time import sleep

import toysynth.synthesis.signal as signal
from toysynth.playback.pyaudio_stream_player import PyAudioStreamPlayer
from toysynth.communication import Mailbox

class Controller(threading.Thread):
    def __init__(self, mailbox: Mailbox, sample_rate, frames_per_chunk):
        super().__init__()
        self.log = logging.getLogger(__name__)
        self.mailbox = mailbox

        # Temp components
        self.sin_osc_a = signal.SinWaveOscillator(sample_rate, frames_per_chunk, default_frequency=220.0)
        self.sin_osc_b = signal.SinWaveOscillator(sample_rate, frames_per_chunk, default_frequency=440.0)
        self.sin_osc_b.set_phase_degrees(45)
        self.amp_osc_a = signal.ConstantValueGenerator(sample_rate, frames_per_chunk)
        self.amp_osc_b = signal.ConstantValueGenerator(sample_rate, frames_per_chunk, 0.5)
        self.sin_mixer = signal.DualMixer(sample_rate, frames_per_chunk, self.sin_osc_a, self.sin_osc_b, self.amp_osc_a, self.amp_osc_b)
        self.noise_gen = signal.NoiseGenerator(sample_rate, frames_per_chunk)
        self.amp_sin_mixer = signal.ConstantValueGenerator(sample_rate, frames_per_chunk)
        self.amp_noise_gen = signal.ConstantValueGenerator(sample_rate, frames_per_chunk, 0.03)
        self.noise_mixer = signal.DualMixer(sample_rate, frames_per_chunk, self.sin_mixer, self.noise_gen, self.amp_sin_mixer, self.amp_noise_gen)
        self.signal_root = self.noise_mixer

        self.stream_player = PyAudioStreamPlayer(sample_rate, frames_per_chunk, iter(self.signal_root))

    def run(self):
        self.stream_player.play()
        should_run = True
        while should_run and self.stream_player.is_active():
            # get() is a blocking call
            if message := self.mailbox.get(): 
                match message.split():
                    case ["exit"]:
                        self.log.debug("Got exit command.")
                        self.stream_player.stop()
                        should_run = False
        return

    

        