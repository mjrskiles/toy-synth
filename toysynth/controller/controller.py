import logging
import threading
from time import sleep

from toysynth.synthesis.signal.generator.sin_wave_oscillator import SinWaveOscillator
from toysynth.playback.pyaudio_stream_player import PyAudioStreamPlayer

class Controller(threading.Thread):
    def __init__(self, sample_rate, frames_per_buffer):
        super().__init__()
        self.log = logging.getLogger(__name__)
        self.oscillator = SinWaveOscillator(sample_rate, frames_per_buffer)
        self.stream_player = PyAudioStreamPlayer(sample_rate, frames_per_buffer, self.oscillator.generator())

    def run(self):
        self.stream_player.play()
        while self.stream_player.is_active():
            sleep(0.1)
        self.stream_player.stop()
        