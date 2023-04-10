import tomli
import json # only using json lib to pretty print the resulting dict

class SettingsReader:
    def __init__(self):
        self.data = {}

    def read(self, filepath):
        with open(filepath, "rb") as f:
            self.data = tomli.load(f)

    def __str__(self):
        return json.dumps(self.data, indent=2, default=str)