from fastapi import WebSocket, WebSocketDisconnect
import asyncio


class WebSocketHandler:
    def __init__(self):
        self._active: dict[str,list[WebSocket]] = {}
        self._message_funcs = []

    async def __call__(self, websocket: WebSocket):
        await self.connect(websocket)
        try:
            while True:
                self.receive(websocket)
        except WebSocketDisconnect:
            self.disconnect(websocket)

    async def receive(self, websocket: WebSocket):
        data = await websocket.receive_json()

        for streams, func in self._message_funcs:
            if not streams or data["stream"] in streams:
                if "websocket" in signature(func).params:
                    func(data["data"], websocket)
                else:
                    func(data["data"]

    def disconnect(self, websocket: WebSocket):
        self._active.remove(websocket)

    async def broadcast(self, stream: str, data: dict):
        await asyncio.gather(
            *[ws.send_json({"stream": stream, "data": data}) for ws in self._active[stream]]
        )

    def on_message(self, streams: str | set[str] | None):
        if not streams:
            streams = None
        elif type(streams) is str:
            streams = {streams}

        def inner(func):
            self._message_funcs.append((streams, func))

            return func

        return inner

    @self.on_message("subscribe")
    def subscribe(self, data, websocket):
        if type(streams := data["streams"]) is str: 
            streams = [streams]
        for stream in streams:
            if stream in self._active:
                self._active[stream].append(websocket)
            else:
                self._active[stream] = [websocket]

    @self.on_message("unsubscribe")
    def unsubscribe(self, data, websocket):
        if type(streams := data["streams"]) is str:
            streams = [streams]
        for stream in streams:
            self._active[stream].remove(websocket)
            
            if not self._active[stream]:
                del self._active[stream]


            
                            
        
