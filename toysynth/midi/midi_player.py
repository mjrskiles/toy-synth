import logging
import threading

import mido

from toysynth.communication import Mailbox
import toysynth.communication.message_builder as mb

class MidiPlayer(threading.Thread):
    def __init__(self, mailbox: Mailbox, midi_listener_mailbox: Mailbox):
        super().__init__()
        self.log = logging.getLogger(__name__)
        self.mailbox = mailbox
        self.midi_listener_mailbox = midi_listener_mailbox
        # self.port = mido.open_output('Midi Player')

    def play_file(self, file_path):
        try:
            midi_file = mido.MidiFile(file_path)
            for msg in midi_file.play():
                self.midi_listener_mailbox.put(msg)
        except:
            self.log.error(f"Couldn't play {file_path}")


    def run(self) -> None:
        should_run = True
        while should_run:
            if mail := self.mailbox.get():
                match mail.split():
                    case ['play', '-f', path]:
                        self.play_file(path)
                    case ['exit']:
                        self.log.info("Got exit command.")
                        should_run = False
        return
