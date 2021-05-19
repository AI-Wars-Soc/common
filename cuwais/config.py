import yaml


class Config:
    def __init__(self, path):
        with open(path, 'r') as stream:
            self.data = yaml.safe_load(stream)

    def get_or_default(self, key, default):
        return self.data.get(key, default)


config_file = Config("config.yml")
