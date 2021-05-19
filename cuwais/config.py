import yaml


class Config:
    def __init__(self, path):
        with open(path, 'r') as stream:
            self._data = yaml.safe_load(stream)

    def get(self, key: str, default=None):
        if not isinstance(key, str):
            raise RuntimeError("Key should be of type str")

        parts = key.split(".")

        data = self._data
        for part in parts:
            if isinstance(data, dict):
                data = data.get(part, None)
            elif isinstance(data, list):
                try:
                    i = int(part)
                except ValueError:
                    return default
                data = None if i >= len(data) or i < 0 else data[i]
            if data is None:
                return default

        types = [str, int, float]
        for t in types:
            if isinstance(default, t):
                return t(data)

        if isinstance(default, bool):
            return str(data)[0].lower() in {"y", "t"}

        return data


config_file = Config("config.yml")
