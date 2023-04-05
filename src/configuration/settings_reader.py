from configparser import SafeConfigParser

class SettingsReader:
    def __init__(self):
        self.data = {}

    def read(self, filepath):
        config = SafeConfigParser()
        config.read(filepath)

        sections = config.sections()
        sections.append('DEFAULT')

        for section in sections:
            items = config.items(section)
            self.data[section] = {}
            for name, value in items:
                self.data[section][name] = value

    def __str__(self):
        section_keys = self.data.keys()
        return_str = ""
        for key in section_keys:
            return_str += f"[{key}]\n"
            section_items = self.data[key].keys()
            for item_key in section_items:
                return_str += f"{item_key}: {self.data[key][item_key]}\n"
        return return_str