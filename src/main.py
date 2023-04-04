from time import sleep

import synth.oscillator.square_wave_oscillator as osc
import synth.sample_player.pyaudio_sample_player as player

sample_rate = 44100

if __name__ == "__main__":
    oscillator = osc.SquareWaveOscillator(sample_rate)
    sample_player = player.PyAudioSamplePlayer(sample_rate)

    sample = oscillator.generate_sample()
    # print(f"sample: {sample}")
    sample_player.load(sample)

    sample_player.play()
    while sample_player.stream.is_active():
        sleep(0.1)
    sample_player.stop()