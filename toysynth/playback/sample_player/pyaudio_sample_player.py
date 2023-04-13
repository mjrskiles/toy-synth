import logging

import pyaudio
import numpy as np

from .sample_player import SamplePlayer

class PyAudioSamplePlayer(SamplePlayer):
    def __init__(self, sample_rate, frames_per_buffer):
        super().__init__()
        self.log = logging.getLogger(__name__)
        self.sample = None
        self.sample_rate = sample_rate
        self.frames_per_buffer = frames_per_buffer
        self.pyaudio_interface = pyaudio.PyAudio()
        self.stream = None
        self.generator = None

    def load(self, sample):
        self.sample = sample

    def stream_generator(self, frame_count):
        sample_index = 0
        rollover_count = 0
        while True:
            sample_frames = self.sample[sample_index:(sample_index + frame_count)]
            if (n := len(sample_frames)) < frame_count:
                rollover_count = frame_count - n
                sample_frames = np.hstack([sample_frames, self.sample[:rollover_count]])
            else:
                rollover_count = 0
            yield sample_frames
            sample_index += frame_count
            if rollover_count != 0:
                sample_index = rollover_count

    def audio_callback(self, in_data, frame_count, time_info, status):
            if self.generator is None:
                self.generator = self.stream_generator(frame_count)
            data = next(self.generator).tobytes()
            return (data, pyaudio.paContinue)       

    def play(self):
        if self.sample is None:
            self.log.error("sample was None!")
            return

        if self.stream is None:
            self.stream = self.pyaudio_interface.open(format = pyaudio.paFloat32,
                                                        channels = 1,
                                                        rate = self.sample_rate,
                                                        output = True,
                                                        stream_callback=self.audio_callback,
                                                        frames_per_buffer=self.frames_per_buffer)

        self.stream.start_stream()
        

    def stop(self):
        if self.stream is None:
            return
        else:
            self.stream.stop_stream()
            self.stream.close()
            self.pyaudio_interface.terminate()
        