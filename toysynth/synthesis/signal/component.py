import logging

class Component():
    def __init__(self, subcomponents) -> None:
        self.log = logging.getLogger(__name__)
        self.subcomponents = subcomponents

    def __iter__(self):
        self._input_iters = [iter(sub) for sub in self.subcomponents]
        return self
    
    def __next__(self):
        self.log.error("Child class should override the __next__ method")
        return