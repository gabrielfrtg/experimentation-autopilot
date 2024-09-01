

class Config:
    """ A simple class to allow dot notation access to dictionary keys """
    def __init__(self, data):
        for key, value in data.items():
            if isinstance(value, dict):
                value = Config(value)
            setattr(self, key, value)

