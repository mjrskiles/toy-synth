import logging

class SamplePlayer:
    def __init__(self):
        self.type = None
        self.log = logging.getLogger(__name__)
    
    def load(self, sample):
        self.log.error(f"attempted to use base class!")

    def play(self):
        self.log.error(f"attempted to use base class!")

    def stop(self):
        self.log.error(f"attempted to use base class!")