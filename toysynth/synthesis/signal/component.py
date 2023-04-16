import logging

class Component():
    def __init__(self) -> None:
        self.log = logging.getLogger(__name__)

    def __iter__(self):
        return self
    
    def __next__(self):
        self.log.error("Child class should override the __next__ method")
        return