import logging
import threading
import queue
import rtmidi
from rtmidi import midiconstants

import toysynth.communication.message_builder as mb
from toysynth.communication import Mailbox


class RTMidiListener(threading.Thread):
    def __init__(self, mailbox: Mailbox, controller_mailbox: Mailbox, port_name):
        super().__init__(name=f"{port_name}-listener")
        self.log = logging.getLogger(__name__)
        self.mailbox = mailbox
        self.controller_mailbox = controller_mailbox
        self.port_name = port_name

    def _midi_callback(self, event, data=None):
        msg, _ = event
        midi_msg = msg[0] & 0xF0

        if midi_msg == midiconstants.NOTE_ON:
            note = msg[1]
            channel = msg[0] & 0x0F
            ctrl_msg = mb.builder().note_on().with_note(note).on_channel(channel)
            self.controller_mailbox.put(str(ctrl_msg))

        elif midi_msg == midiconstants.NOTE_OFF:
            note = msg[1]
            channel = msg[0] & 0x0F
            ctrl_msg = mb.builder().note_off().with_note(note).on_channel(channel)
            self.controller_mailbox.put(str(ctrl_msg))

        elif midi_msg == midiconstants.CONTROL_CHANGE:
            channel = msg[0] & 0x0F
            control_num = msg[1]
            value = msg[2]
            ctrl_msg = mb.builder().control_change().on_channel(channel).with_control_num(control_num).with_value(value)
            self.controller_mailbox.put(str(ctrl_msg))

        else:
            self.log.info(f"Matched unknown MIDI message: {msg}")


    def run(self):
        should_run = True
        midi_in = rtmidi.MidiIn()
        port_index = -1

        for i in range(midi_in.get_port_count()):
            if midi_in.get_port_name(i) == self.port_name:
                port_index = i
                break

        if port_index == -1:
            self.log.error(f"Port {self.port_name} not found")
            return

        midi_in.set_callback(self._midi_callback)
        midi_in.open_port(port_index)
        self.log.info(f"Opened port {self.port_name}")

        while should_run:
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

        midi_in.close_port()
        self.log.info(f"Closed port {self.port_name}")
