class cached_classproperty:
    """
    Adapted from https://github.com/hottwaj/classproperties
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, _, cls):
        setattr(cls, self.func.__name__, val := self.func(cls))

        return val
