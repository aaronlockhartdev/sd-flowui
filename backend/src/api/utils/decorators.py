import os
import contextlib
import functools


class cached_classproperty:
    """
    Adapted from https://github.com/hottwaj/classproperties
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, _, cls):
        setattr(cls, self.func.__name__, val := self.func(cls))

        return val


class suppress_std:
    """
    Adapted from https://stackoverflow.com/a/28321717
    """

    def __init__(self, func):
        self.func = func

        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        with open(os.devnull, "w") as devnull:
            with contextlib.redirect_stdout(devnull), contextlib.redirect_stderr(
                devnull
            ):
                return self.func(*args, **kwargs)
