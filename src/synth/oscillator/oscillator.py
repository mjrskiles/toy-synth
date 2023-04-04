class Oscillator:
    def __init__(self):
        self._type = None

    @property
    def type(self):
        """The Oscillator Type"""
        return self._type
        
    def generate_sample(self):
        print("[generate_sample] Tried to use the oscillator base class!")
    