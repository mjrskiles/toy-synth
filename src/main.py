from time import sleep

import synth.oscillator.square_wave_oscillator as osc
import synth.sample_player.pyaudio_sample_player as player
import configuration.settings_reader as sr

if __name__ == "__main__":
    settings = sr.SettingsReader()
    settings.read("./settings.ini")

    sample_rate = int(settings.data['synthesis']['sample_rate'])
    sample_buffer_target_size = int(settings.data['synthesis']['sample_buffer_target_size'])
    oscillator = osc.SquareWaveOscillator(sample_rate, sample_buffer_target_size)
    sample_player = player.PyAudioSamplePlayer(sample_rate)

    sample = oscillator.generate_sample()
    # print(f"sample: {sample}")
    sample_player.load(sample)

    sample_player.play()
    while sample_player.stream.is_active():
        sleep(0.1)
    sample_player.stop()