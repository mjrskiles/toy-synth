import numpy as np
import pyaudio
from pynput import keyboard

# Parameters
sample_rate = 44100  # samples per second
freq = 440.0  # frequency of the square wave (in Hz)
volume = 0.5  # initial volume (range: 0.0 to 1.0)

# Global variable to keep track of space bar state
space_pressed = False

# Callback function for PyAudio stream
def audio_callback(in_data, frame_count, time_info, status):
    t = np.linspace(0, frame_count / sample_rate, frame_count, endpoint=False)
    square_wave = np.sign(np.sin(2 * np.pi * freq * t)) * volume
    output_data = square_wave.astype(np.float32).tobytes()

    global space_pressed
    if space_pressed:
        return (output_data, pyaudio.paContinue)
    else:
        return (b'\x00' * len(output_data), pyaudio.paContinue)

# Define key press and release event handlers for pynput
def on_press(key):
    global space_pressed
    if key == keyboard.Key.space:
        space_pressed = True

def on_release(key):
    global space_pressed
    if key == keyboard.Key.space:
        space_pressed = False
    elif key == keyboard.Key.esc:
        return False

if __name__ == "__main__":
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paFloat32,
                    channels=1,
                    rate=sample_rate,
                    output=True,
                    stream_callback=audio_callback)

    # Start the stream
    stream.start_stream()

    # Set up the pynput listener
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    # Clean up
    stream.stop_stream()
    stream.close()
    p.terminate()
