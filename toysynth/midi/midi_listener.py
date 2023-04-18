import logging
import threading

import mido

import toysynth.communication.message_builder as mb
from toysynth.communication import Mailbox

class MidiListener(threading.Thread):
    def __init__(self, mailbox: Mailbox, controller_mailbox: Mailbox):
        super().__init__()
        self.log = logging.getLogger(__name__)
        self.mailbox = mailbox
        self.controller_mailbox = controller_mailbox
    
    def run(self):
        should_run = True
        # inport = mido.open_input()
        while should_run:
            # iter_pending won't block
            # for msg in inport.iter_pending():
            #     match msg.type:
            #         case 'note_on':
            #             ctrl_msg = mb.builder().note_on().with_note(msg.note)
            #             self.controller_mailbox.put(ctrl_msg)
            #         case 'note_off':
            #             ctrl_msg = mb.builder().note_off().with_note(msg.note)
            #             self.controller_mailbox.put(ctrl_msg)
            #         case _:
            #             self.log.info(f"Matched unknown MIDI message: {msg}")
            
            if mail := self.mailbox.get():
                if isinstance(mail, mido.Message):
                    # self.log.debug(f"got midi command: {mail}")
                    match mail.type:
                        case "note_on":
                            ctrl_msg = mb.builder().note_on().with_note(mail.note).on_channel(mail.channel)
                            self.controller_mailbox.put(str(ctrl_msg))
                        case "note_off":
                            # self.log.debug(f"got note off command: {mail}")
                            ctrl_msg = mb.builder().note_off().with_note(mail.note).on_channel(mail.channel)
                            self.controller_mailbox.put(str(ctrl_msg))
                        case _:
                            self.log.info(f"Matched unknown MIDI message: {mail}")
                elif isinstance(mail, str):
                    match mail.split():
                        case ['exit']:
                            self.log.info("Got exit command.")
                            should_run = False
                        case _:
                            self.log.info(f"Matched unknown mailbox message: {mail}")
            
        return