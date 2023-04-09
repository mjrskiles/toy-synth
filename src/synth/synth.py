import threading
from time import sleep

from synth.oscillator.square_wave_oscillator import SquareWaveOscillator
from synth.sample_player.pyaudio_sample_player import PyAudioSamplePlayer

class Synth(threading.Thread):
    def __init__(self, command_queue, sample_rate, sample_buffer_target_size, frames_per_buffer):
        super().__init__()
        self.command_queue = command_queue
        self.sample_rate = sample_rate
        self.sample_buffer_target_size = sample_buffer_target_size
        self.frames_per_buffer = frames_per_buffer
        self.oscillator = SquareWaveOscillator(self.sample_rate, self.sample_buffer_target_size)
        self.sample_player = PyAudioSamplePlayer(self.sample_rate, self.frames_per_buffer)
        self.sample = self.oscillator.generate_sample()
        self.sample_player.load(self.sample)

    def run(self):
        self.sample_player.play()
        while self.sample_player.stream.is_active():
            if command := self.command_queue.get():
                print(f"{__name__}: [run] Got command!")
                try:
                    parsed_float = float(command)
                    self.oscillator.frequency = parsed_float
                    self.sample = self.oscillator.generate_sample()
                    self.sample_player.load(self.sample)
                except:
                    print(f"{__name__}: [run] Couldn't parse float")
            sleep(0.1)
        self.sample_player.stop()
