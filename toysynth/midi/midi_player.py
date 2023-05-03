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

    def play_file(self, file_path):
        try:
            midi_file = mido.MidiFile(file_path)

            # Send a message to the synth to play in either mono or poly mode depending on the midi file type
            self.log.info(f"Opened MIDI file type {midi_file.type}")
            cc_num = 127 if midi_file.type == 0 else 126
            mono_poly_msg = mido.Message("control_change", channel=0, control=cc_num, value=0)
            self.port.send(mono_poly_msg)
            
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
