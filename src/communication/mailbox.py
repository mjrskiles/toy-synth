import queue

class Mailbox(queue.Queue):
    def __init__(self):
        super().__init__()
        