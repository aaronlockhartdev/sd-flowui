from inspect import signature
from fastapi import WebSocket, WebSocketDisconnect
import asyncio


class WebSocketHandler:
    def __init__(self):
        self._active: dict[WebSocket, set[str]] = {}
        self._on_message: dict[str, list[function]] = {"*": []}

        @self.on_message("subscribe")
        def subscribe(data, websocket):
            for stream in data["streams"]:
                if stream in self._active:
                    self._active[websocket].add(stream)
                else:
                    self._active[websocket] = {stream}

        setattr(self, "subscribe", subscribe)

        @self.on_message("unsubscribe")
        def unsubscribe(data, websocket):
            for stream in data["streams"]:
                self._active[websocket].remove(stream)

                if not self._active[websocket]:
                    del self._active[websocket]

        setattr(self, "unsubscribe", unsubscribe)

    async def __call__(self, websocket: WebSocket):
        await self.connect(websocket)
        try:
            while True:
                await self.receive(websocket)
        except WebSocketDisconnect:
            self.disconnect(websocket)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

    def disconnect(self, websocket: WebSocket):
        if websocket in self._active:
            del self._active[websocket]

    async def broadcast(self, stream: str, data: dict):
        await asyncio.gather(
            *[
                k.send_json({"stream": stream, "data": data})
                for k, v in self._active.items()
                if stream in v
            ]
        )

    async def receive(self, websocket: WebSocket):
        data = await websocket.receive_json()

        print(data)

        for func in self._on_message[data["stream"]] + self._on_message["*"]:
            if "websocket" in signature(func).parameters:
                func(data["data"], websocket)
            else:
                func(data["data"])

    def on_message(self, stream: str | None):
        def inner(func):
            nonlocal stream

            if stream in self._on_message:
                self._on_message[stream].append(func)
            else:
                self._on_message[stream] = [func]

            return func

        return inner


websocket_handler = WebSocketHandler()
