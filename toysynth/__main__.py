import os
import logging
import sys

from .configuration import SettingsReader
from .communication import MQTTListener, Mailbox
from .controller import Controller
from .midi import MidiPlayer, MidiListener

if __name__ == "__main__":
    log = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s [%(levelname)s] %(module)s [%(funcName)s]: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
    
    # Fetch static data from settings.toml
    main_script_dir = os.path.dirname(os.path.realpath(__file__))
    full_settings_path = os.path.join(main_script_dir, "settings.toml")
    log.info(f"Launching toy synth with settings from {full_settings_path}")

    settings = SettingsReader()
    settings.read(full_settings_path)
    log.debug(f"App settings: {str(settings)}")

    # Set up the command queues
    main_mailbox = Mailbox()
    controller_mailbox = Mailbox()
    midi_listener_mailbox = Mailbox()
    midi_player_mailbox = Mailbox()

    # Set up the Synth
    sample_rate = int(settings.data['synthesis']['sample_rate'])
    sample_buffer_target_size = int(settings.data['synthesis']['sample_buffer_target_size'])
    frames_per_chunk = int(settings.data['synthesis']['frames_per_chunk'])

    toy_synth = Controller(controller_mailbox, sample_rate, frames_per_chunk)
    
    # Open the MQTT listener
    mqtt_host = settings.data['mqtt']['host']
    mqtt_port = int(settings.data['mqtt']['port'])

    topics = [topic['path'] for topic in settings.data['mqtt']['topics']]
    mqtt_listener = MQTTListener(mqtt_host, mqtt_port, topics, {"toy/synth/test/command": controller_mailbox, "toy/exit": main_mailbox, "toy/midi/player": midi_player_mailbox})

    # Create the MIDI threads
    player_port_name = settings.data['midi']['player_port_name']
    midi_listener = MidiListener(midi_listener_mailbox, controller_mailbox, player_port_name)
    midi_player = MidiPlayer(midi_player_mailbox, player_port_name)

    try:
        # Start the threads
        toy_synth.start()
        mqtt_listener.start()
        midi_player.start()
        midi_listener.start()

        # main thread loop
        should_run = True
        while should_run:
            if message := main_mailbox.get():
                match message.split():
                    case ["exit"]:
                        should_run = False
                    case _:
                        log.info(f"Received unhandled message on main thread: {message}")

    except KeyboardInterrupt:
        log.info("Caught Keyboard interrupt. Shutting down.")
    
    # Send the exit command to the various threads
    controller_mailbox.put("exit")
    midi_player_mailbox.put("exit")
    midi_listener_mailbox.put("exit")

    toy_synth.join()
    mqtt_listener.stop()
    mqtt_listener.join()
    midi_player.join()
    midi_listener.join()
    sys.exit(0)