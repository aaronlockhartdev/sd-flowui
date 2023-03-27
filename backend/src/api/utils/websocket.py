from fastapi import WebSocket, WebSocketDisconnect
import asyncio


class WebSocketHandler:
    def __init__(self):
        self._active: list[WebSocket] = []
        self._connect_funcs = []
        self._message_funcs = []

    async def __call__(self, websocket: WebSocket):
        await self.connect(websocket)
        try:
            while True:
                self.receive(websocket)
        except WebSocketDisconnect:
            self.disconnect(websocket)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self._active.append(websocket)

        await asyncio.gather(
            *[
                websocket.send_json({"stream": s, "data": f()})
                for s, f in self._on_connect
            ]
        )

    async def receive(self, websocket: WebSocket):
        data = await websocket.receive_json()

        for streams, func in self._message_funcs:
            if not streams or data["stream"] in streams:
                func(data["data"])

    def disconnect(self, websocket: WebSocket):
        self._active.remove(websocket)

    async def broadcast(self, stream: str, data: dict):
        await asyncio.gather(
            *[ws.send_json({"stream": stream, "data": data}) for ws in self._active]
        )

    def on_connect(self, stream: str):
        def inner(func):
            self._on_connect.append((stream, func))

            return func

        return inner

    def on_message(self, streams: str | set[str] | None):
        if not streams:
            streams = None
        elif type(streams) is str:
            streams = {streams}

        def inner(func):
            self._message_funcs.append((streams, func))

            return func

        return inner
