from fastapi import WebSocket
import asyncio


class WebSocketHandler:
    def __init__(self):
        self.active: list[WebSocket] = []
        self.on_connect = []
        self.on_message = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)

        await asyncio.gather(
            *[
                websocket.send_json({"stream": s, "data": f()})
                for s, f in self.on_connect
            ]
        )

    async def receive(self, websocket: WebSocket):
        data = await websocket.receive_json()

        for streams, func in self.on_message:
            if data["stream"] in streams:
                func(data["data"])

    def disconnect(self, websocket: WebSocket):
        self.active.remove(websocket)

    async def broadcast(self, stream: str, data: dict):
        await asyncio.gather(
            *[ws.send_json({"stream": stream, "data": data}) for ws in self.active]
        )


handler = WebSocketHandler()


def on_connect(stream: str):
    def inner(func):
        handler.on_connect.append((stream, func))

        return func

    return inner


def on_message(streams: str | set[str] | None):
    if not streams:
        streams = None
    elif type(streams) is str:
        streams = {streams}

    def inner(func):
        handler.on_message.append((streams, func))

        return func

    return inner
