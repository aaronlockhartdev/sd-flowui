from os import environ as env
import asyncio

from watchfiles import awatch

import api.utils as utils


class FileWatcher:
    def __init__(self):
        self._stop_event = asyncio.Event()

    async def __call__(self):
        async for events in awatch(env["DATA_DIR"], stop_event=self.stop_event):
            pass

    def stop(self):
        self._stop_event.set()
