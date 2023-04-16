import logging
import threading
from time import sleep

from toysynth.synthesis.signal.sin_wave_oscillator import SinWaveOscillator
from toysynth.synthesis.signal.square_wave_oscillator import SquareWaveOscillator
from toysynth.playback.pyaudio_stream_player import PyAudioStreamPlayer
from toysynth.communication import Mailbox

class Controller(threading.Thread):
    def __init__(self, mailbox: Mailbox, sample_rate, frames_per_chunk):
        super().__init__()
        self.log = logging.getLogger(__name__)
        self.mailbox = mailbox
        self.phase_mod = SinWaveOscillator(sample_rate, frames_per_chunk, None, default_frequency=0.5)
        self.oscillator = SinWaveOscillator(sample_rate, frames_per_chunk, self.phase_mod, default_frequency=440.0)
        # self.oscillator = SquareWaveOscillator(sample_rate, frames_per_chunk)
        self.stream_player = PyAudioStreamPlayer(sample_rate, frames_per_chunk, iter(self.oscillator))

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

    

        