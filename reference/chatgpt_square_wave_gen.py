import numpy as np
import pyaudio
import time

# Parameters
sample_rate = 44100  # samples per second
freq = 440.0  # frequency of the square wave (in Hz)
volume = 0.5  # initial volume (range: 0.0 to 1.0)

# Generate a square wave with the given frequency and volume
def generate_square_wave(freq, volume, sample_rate):
    samples_per_cycle = int(sample_rate / freq)
    square_wave = np.hstack([np.ones(samples_per_cycle // 2) * volume, np.ones(samples_per_cycle // 2) * -volume])
    return square_wave.astype(np.float32)

# Callback function for PyAudio stream
def audio_callback(in_data, frame_count, time_info, status):
    global square_wave
    output_data = square_wave[:frame_count].tobytes()
    return (output_data, pyaudio.paContinue)

if __name__ == "__main__":
    square_wave = generate_square_wave(freq, volume, sample_rate)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=sample_rate,
                    output=True,
                    stream_callback=audio_callback)

    # Start the stream
    stream.start_stream()

    # Keep the script running while the stream is active
    try:
        while stream.is_active():
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass

    # Clean up
    stream.stop_stream()
    stream.close()
    p.terminate()
