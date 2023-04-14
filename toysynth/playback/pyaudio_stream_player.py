import pyaudio

from .stream_player import StreamPlayer

class PyAudioStreamPlayer(StreamPlayer):
    def __init__(self, sample_rate, frames_per_chunk, input_delegate):
        super().__init__(sample_rate, frames_per_chunk, input_delegate)
        self.pyaudio_interface = pyaudio.PyAudio()
        self._output_stream = None

    def play(self):
        if self._output_stream is None:
            self._output_stream = self.pyaudio_interface.open(format = pyaudio.paFloat32,
                                                        channels = 1,
                                                        rate = self.sample_rate,
                                                        output = True,
                                                        stream_callback=self.audio_callback,
                                                        frames_per_buffer=self.frames_per_chunk)

        self._output_stream.start_stream()
    
    def stop(self):
        if self._output_stream is None:
            return
        else:
            self._output_stream.stop_stream()
            self._output_stream.close()
            self.pyaudio_interface.terminate()

    def audio_callback(self, in_data, frame_count, time_info, status):
        """
        The audio callback should just have to call next() on the input delegate
        """
        frames = next(self.input_delegate)
        return (frames, pyaudio.paContinue)
    
    def is_active(self):
        if self._output_stream is None:
            return False
        
        return self._output_stream.is_active()