import logging
import threading
import queue

import mido

import toysynth.communication.message_builder as mb
from toysynth.communication import Mailbox

class MidiListener(threading.Thread):
    def __init__(self, mailbox: Mailbox, controller_mailbox: Mailbox, player_port_name):
        super().__init__()
        self.log = logging.getLogger(__name__)
        self.mailbox = mailbox
        self.controller_mailbox = controller_mailbox
        self.player_port_name = player_port_name
    
    def run(self):
        should_run = True
        inport = mido.open_input(self.player_port_name)
        self.log.info(f"Available MIDI input ports: {mido.get_input_names()}")
        while should_run:
            # iter_pending won't block
            if msg := inport.receive():
                match msg.type:
                    case "note_on":
                        ctrl_msg = mb.builder().note_on().with_note(msg.note).on_channel(msg.channel)
                        self.controller_mailbox.put(str(ctrl_msg))
                    case "note_off":
                        ctrl_msg = mb.builder().note_off().with_note(msg.note).on_channel(msg.channel)
                        self.controller_mailbox.put(str(ctrl_msg))
                    case "stop":
                        self.log.info(f"Received midi STOP message")
                    case _:
                        self.log.info(f"Matched unknown MIDI message: {msg}")
            
            # get and get_nowait both raise queue.Empty exception if there is nothing int he queue
            try:
                if mail := self.mailbox.get_nowait():
                    match mail.split():
                        case ['exit']:
                            self.log.info("Got exit command.")
                            should_run = False
                        case _:
                            self.log.info(f"Matched unknown mailbox message: {mail}")
            except queue.Empty:
                pass
        return