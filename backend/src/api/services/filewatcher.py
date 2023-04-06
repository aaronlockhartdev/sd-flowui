import os
import asyncio

from os import environ as env
from watchfiles import awatch

from .websocket import websocket_handler


class FileWatcher:
    def __init__(self):
        self._stop_event = asyncio.Event()

        self.dir_structure = self._read_dir(os.path.normpath(env["DATA_DIR"]))

    async def watch(self):
        async for _ in awatch(env["DATA_DIR"], stop_event=self._stop_event):
            self.dir_structure = self._read_dir(os.path.normpath(env["DATA_DIR"]))
            await websocket_handler.broadcast("files", self.dir_structure)

    def stop(self):
        self._stop_event.set()

    @staticmethod
    def _read_dir(path):
        return {
            x: (
                None
                if os.path.isfile(path_ := os.path.join(path, x))
                else FileWatcher._read_dir(path_)
            )
            for x in os.listdir(path)
        }


file_watcher = FileWatcher()
