import logging
import threading

import mido

from toysynth.communication import Mailbox
import toysynth.communication.message_builder as mb

class MidiPlayer(threading.Thread):
    def __init__(self, mailbox: Mailbox, port_name):
        super().__init__()
        self.log = logging.getLogger(__name__)
        self.mailbox = mailbox
        self.port = mido.open_output(port_name, virtual=True)
        self.log.info(f"Available MIDI output ports: {mido.get_output_names()}")

    def play_file(self, file_path):
        try:
            midi_file = mido.MidiFile(file_path)
            for msg in midi_file.play():
                self.port.send(msg)
        except Exception as err:
            self.log.error(f"Couldn't play {file_path}")
            self.log.error(f"Caught exception: {err}")


    def run(self) -> None:
        should_run = True
        while should_run:
            if mail := self.mailbox.get():
                match mail.split():
                    case ['play', '-f', path]:
                        self.play_file(path)
                    case ['exit']:
                        self.log.info("Got exit command.")
                        self.port.send(mido.Message('stop'))
                        should_run = False
        return
