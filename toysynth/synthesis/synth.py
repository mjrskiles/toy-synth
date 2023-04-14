import threading
from time import sleep
import logging

from .oscillator.square_wave_oscillator import SquareWaveOscillator
from toysynth.playback.sample_player.pyaudio_sample_player import PyAudioSamplePlayer

class Synth(threading.Thread):
    def __init__(self, command_queue, sample_rate, sample_buffer_target_size, frames_per_chunk):
        super().__init__()
        self.log = logging.getLogger(__name__)
        self.command_queue = command_queue
        self.sample_rate = sample_rate
        self.sample_buffer_target_size = sample_buffer_target_size
        self.frames_per_chunk = frames_per_chunk
        self.oscillator = SquareWaveOscillator(self.sample_rate, self.sample_buffer_target_size)
        self.sample_player = PyAudioSamplePlayer(self.sample_rate, self.frames_per_chunk)
        self.sample = self.oscillator.generate_sample()
        self.sample_player.load(self.sample)

    def run(self):
        self.sample_player.play()
        while self.sample_player.stream.is_active():
            if command := self.command_queue.get():
                self.log.debug(f"Got command: {command}")
                match command.split():
                    case ["note_on", "-f", freq]:
                        self.set_frequency(freq)
                    case ["note_off"]:
                        self.set_frequency(0.0)
                    case _:
                        self.log.warning(f"failed to match command")
            sleep(0.1)
        self.sample_player.stop()

    def stop(self):
        self.sample_player.stop()

    def set_frequency(self, frequency):
        try:
            parsed_float = float(frequency)
            self.oscillator.frequency = parsed_float
            self.sample = self.oscillator.generate_sample()
            self.sample_player.load(self.sample)
        except:
            self.log.error(f"Couldn't parse float")

