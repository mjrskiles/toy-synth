class SamplePlayer:
    def __init__(self):
        self.type = None
    
    def load(self, sample):
        print("[load] attempted to use base class!")

    def play(self):
        print("[play] attempted to use base class!")

    def stop(self):
        print("[stop] attempted to use base class!")