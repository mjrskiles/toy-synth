class ActionHandler():
    def __init__(self):
        self._on_action_start = lambda : print(f"{__name__}: on_action_start default function invoked")
        self._on_action_update = lambda : print(f"{__name__}: on_action_update default function invoked")
        self._on_action_end = lambda : print(f"{__name__}: on_action_end default function invoked")

    @property
    def on_action_start(self):
        return self._on_action_start

    @on_action_start.setter
    def on_action_start(self, value):
        if callable(value):
            self._on_action_start = value
        else:
            print(f"{__name__}: [on_action_start] can't set with value {value}")

    @property
    def on_action_update(self):
        return self._on_action_update

    @on_action_update.setter
    def on_action_update(self, value):
        if callable(value):
            self._on_action_update = value
        else:
            print(f"{__name__}: [on_action_update] can't set with value {value}")

    @property
    def on_action_end(self):
        return self._on_action_end

    @on_action_end.setter
    def on_action_end(self, value):
        if callable(value):
            self._on_action_end = value
        else:
            print(f"{__name__}: [on_action_end] can't set with value {value}")



    