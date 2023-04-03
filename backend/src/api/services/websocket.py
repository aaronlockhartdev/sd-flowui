from inspect import signature
from fastapi import WebSocket, WebSocketDisconnect
import asyncio


class WebSocketHandler:
    def __init__(self):
        self._active: dict[WebSocket, set[str]] = dict()
        self._on_message: dict[str, list[function]] = dict()

        @self.on_message("subscribe")
        def _(data, websocket):
            for stream in data["streams"]:
                if data["action"] == "subscribe":
                    if websocket in self._active:
                        self._active[websocket].add(stream)
                    else:
                        self._active[websocket] = {stream}
                elif data["action"] == "unsubscribe":
                    self._active[websocket].remove(stream)

            if websocket in self._active and not self._active[websocket]:
                del self._active[websocket]

    async def listen(self, websocket: WebSocket):
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
        msg = await websocket.receive_json()

        for func in self._on_message[msg["stream"]]:
            if "websocket" in signature(func).parameters:
                func(msg["data"], websocket)
            else:
                func(msg["data"])

    def on_message(self, stream: str):
        def decorator(func):
            nonlocal stream

            if stream in self._on_message:
                self._on_message[stream].append(func)
            else:
                self._on_message[stream] = [func]

            return func

        return decorator


websocket_handler = WebSocketHandler()
