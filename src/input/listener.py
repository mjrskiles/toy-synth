from pynput import keyboard

import input.action_handler as ah

class Listener():
    def __init__(self, action_handler):
        self._action_handler = action_handler

    @property
    def action_handler(self):
        return self._action_handler

    @action_handler.setter
    def action_handler(self, value):
        if isinstance(value, ah.ActionHandler):
            self._action_handler = value
        else:
            print(f"{__name__}: action_handler couldn't set value {value}")

    def listen(self):
        print(f"{__name__}: [listen] attempted to use base class")

class KeyboardListener(Listener):
    def __init__(self, action_handler):
        super().__init__(action_handler)

    
    

