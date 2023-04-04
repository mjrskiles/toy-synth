import pyaudio

import synth.sample_player.sample_player as player

class PyAudioSamplePlayer(player.SamplePlayer):
    def __init__(self, sample_rate):
        super().__init__()
        self.sample = None
        self.sample_rate = sample_rate
        self.pyaudio_interface = pyaudio.PyAudio()
        self.stream = None

    def load(self, sample):
        self.sample = sample

    def play(self):
        if self.sample is None:
            print("[play] sample was None!")
            return

        def audio_callback(in_data, frame_count, time_info, status):
            data = self.sample[:frame_count].tobytes()
            return (data, pyaudio.paContinue)

        if self.stream is None:
            self.stream = self.pyaudio_interface.open(format = pyaudio.paFloat32,
                                                        channels = 1,
                                                        rate = self.sample_rate,
                                                        output = True,
                                                        stream_callback=audio_callback)

        self.stream.start_stream()
        

    def stop(self):
        if self.stream is None:
            return
        else:
            self.stream.stop_stream()
            self.stream.close()
            self.pyaudio_interface.terminate()
        