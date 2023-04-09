from time import sleep
import os
import queue
import sys
import signal

import synth
import configuration.settings_reader as sr
import communication

if __name__ == "__main__":
    # Fetch static data from settings.ini
    main_script_dir = os.path.dirname(os.path.realpath(__file__))
    full_settings_path = main_script_dir + "/settings.ini"

    settings = sr.SettingsReader()
    settings.read(full_settings_path)

    # Set up the command queues
    synth_queue = communication.Mailbox()

    # Set up the Synth
    sample_rate = int(settings.data['synthesis']['sample_rate'])
    sample_buffer_target_size = int(settings.data['synthesis']['sample_buffer_target_size'])
    frames_per_buffer = int(settings.data['synthesis']['frames_per_buffer'])

    toy_synth = synth.Synth(synth_queue, sample_rate, sample_buffer_target_size, frames_per_buffer)
    
    # Open the MQTT listener
    mqtt_host = settings.data['mqtt']['host']
    mqtt_port = int(settings.data['mqtt']['port'])

    topics = [
        "toy/exit",
        "toy/log",  
        "toy/synth/test/command"
        ]
    mqtt_listener = communication.MQTTListener(mqtt_host, mqtt_port, topics, {"toy/synth/test/command": synth_queue})

    # Start the threads
    toy_synth.start()
    mqtt_listener.start()

    mqtt_listener.join()