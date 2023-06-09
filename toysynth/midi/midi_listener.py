import logging
import threading
import queue

import mido

import toysynth.communication.message_builder as mb
from toysynth.communication import Mailbox

class MidiListener(threading.Thread):
    def __init__(self, mailbox: Mailbox, controller_mailbox: Mailbox, port_name):
        super().__init__(name=f"{port_name}-listener")
        self.log = logging.getLogger(__name__)
        self.mailbox = mailbox
        self.controller_mailbox = controller_mailbox
        self.port_name = port_name
    
    def run(self):
        should_run = True
        inport = mido.open_input(self.port_name)
        self.log.info(f"Opened port {self.port_name}")
        while should_run:
            if msg := inport.receive():
                match msg.type:
                    case "note_on":
                        ctrl_msg = mb.builder().note_on().with_note(msg.note).on_channel(msg.channel)
                        self.controller_mailbox.put(str(ctrl_msg))
                    case "note_off":
                        ctrl_msg = mb.builder().note_off().with_note(msg.note).on_channel(msg.channel)
                        self.controller_mailbox.put(str(ctrl_msg))
                    case "control_change":
                        ctrl_msg = mb.builder().control_change().on_channel(msg.channel).with_control_num(msg.control).with_value(msg.value)
                        # self.log.debug(f"Received CC : {msg} and translated to : {ctrl_msg}")
                        self.controller_mailbox.put(str(ctrl_msg))
                    case "program_change":
                        ctrl_msg = mb.builder().program_change().on_channel(msg.channel).with_program_num(msg.program)
                        self.controller_mailbox.put(str(ctrl_msg))
                    case "stop":
                        self.log.info(f"Received midi STOP message")
                    case _:
                        self.log.info(f"Matched unknown MIDI message: {msg}")
            
            # get_nowait raises queue.Empty exception if there is nothing int he queue
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