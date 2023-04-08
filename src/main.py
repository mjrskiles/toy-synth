from time import sleep
import os

import synth.oscillator.square_wave_oscillator as osc
import synth.sample_player.pyaudio_sample_player as player
import configuration.settings_reader as sr

if __name__ == "__main__":
    main_script_dir = os.path.dirname(os.path.realpath(__file__))
    full_settings_path = main_script_dir + "/settings.ini"

    settings = sr.SettingsReader()
    settings.read(full_settings_path)

    sample_rate = int(settings.data['synthesis']['sample_rate'])
    sample_buffer_target_size = int(settings.data['synthesis']['sample_buffer_target_size'])
    frames_per_buffer = int(settings.data['synthesis']['frames_per_buffer'])
    oscillator = osc.SquareWaveOscillator(sample_rate, sample_buffer_target_size)
    sample_player = player.PyAudioSamplePlayer(sample_rate, frames_per_buffer)

    sample = oscillator.generate_sample()
    # print(f"sample: {sample}")
    sample_player.load(sample)

    sample_player.play()
    while sample_player.stream.is_active():
        sleep(0.1)
    sample_player.stop()