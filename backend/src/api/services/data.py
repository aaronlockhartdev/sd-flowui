from os import environ as env
import asyncio
from watchfiles import awatch


class FileWatcher:
    def __init__(self):
        self._stop_event = asyncio.Event()

    async def watch(self):
        async for events in awatch(env["DATA_DIR"], stop_event=self._stop_event):
            pass

    def stop(self):
        self._stop_event.set()


file_watcher = FileWatcher()
