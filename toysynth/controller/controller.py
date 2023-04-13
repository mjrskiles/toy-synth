import logging
import threading
from time import sleep

from toysynth.synthesis.signal.generator.sin_wave_oscillator import SinWaveOscillator
from toysynth.playback.pyaudio_stream_player import PyAudioStreamPlayer
from toysynth.communication import Mailbox

class Controller(threading.Thread):
    def __init__(self, mailbox: Mailbox, sample_rate, frames_per_buffer):
        super().__init__()
        self.log = logging.getLogger(__name__)
        self.mailbox = mailbox
        self.oscillator = SinWaveOscillator(sample_rate, frames_per_buffer)
        self.stream_player = PyAudioStreamPlayer(sample_rate, frames_per_buffer, self.oscillator.generator())

    def run(self):
        self.stream_player.play()
        should_run = True
        while should_run and self.stream_player.is_active():
            if message := self.mailbox.get():
                match message.split():
                    case ["exit"]:
                        self.log.debug("Got exit command.")
                        self.stream_player.stop()
                        should_run = False
            sleep(0.1)
        return

    

        