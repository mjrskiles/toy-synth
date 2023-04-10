import tomli

class SettingsReader:
    def __init__(self):
        self.data = {}

    def read(self, filepath):
        with open(filepath, "rb") as f:
            self.data = tomli.load(f)

    def __str__(self):
        return str(self.data)