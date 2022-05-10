import json

settings_file = 'config.json'

class Config:

    def __init__(self, file:str=settings_file):
        # Load settings
        with open(file) as f:
            self._config = json.load(f)
        self._file = file

    def _save_config(self):
        with open(self._file, 'w') as f:
            json.dump(self._config, f)

    def get(self, key:str):
        try:
            return self._config[key]
        except KeyError:
            return None

    def set(self, key:str, value):
        self._config[key] = value
        self._save_config()