import asyncio
import time
from itertools import islice


def chunks(iterator, size):
    """Yield successive n-sized chunks from an iterator."""
    iterator = iter(iterator)
    while True:
        chunk = list(islice(iterator, size))
        if not chunk:
            break
        yield chunk


def run_async(coro):
    """Run an async function in a synchronous context."""
    try:
        _ = asyncio.get_running_loop()
        return asyncio.create_task(coro)
    except RuntimeError:
        return asyncio.run(coro)


class TimingMixin:
    def _start_timer(self):
        self.start_time = time.perf_counter()

    def _stop_timer(self):
        self.end_time = time.perf_counter()
        self._duration = self.end_time - self.start_time

    def get_duration(self) -> float | None:
        return getattr(self, "_duration", None)


class MenuError(Exception):
    """Custom exception for the Menu class."""


class OptionAlreadyExistsError(MenuError):
    """Exception raised when an option with the same key already exists in the menu."""


class InvalidHookError(MenuError):
    """Exception raised when a hook is not callable."""


class InvalidActionError(MenuError):
    """Exception raised when an action is not callable."""


class NotAMenuError(MenuError):
    """Exception raised when the provided submenu is not an instance of Menu."""


class CaseInsensitiveDict(dict):
    """A case-insensitive dictionary that treats all keys as uppercase."""

    def __setitem__(self, key, value):
        super().__setitem__(key.upper(), value)

    def __getitem__(self, key):
        return super().__getitem__(key.upper())

    def __contains__(self, key):
        return super().__contains__(key.upper())

    def get(self, key, default=None):
        return super().get(key.upper(), default)

    def pop(self, key, default=None):
        return super().pop(key.upper(), default)

    def update(self, other=None, **kwargs):
        if other:
            other = {k.upper(): v for k, v in other.items()}
        kwargs = {k.upper(): v for k, v in kwargs.items()}
        super().update(other, **kwargs)
