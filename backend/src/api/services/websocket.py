import inspect
import asyncio
import functools

from typing import get_type_hints, Any

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel


class WebSocketMsg(BaseModel):
    stream: str
    data: dict[str, Any]


class WebSocketHandler:
    def __init__(self):
        self._active: dict[WebSocket, set[str]] = dict()
        self._on_message: dict[str, list[function]] = dict()

        @self.on_message("streams")
        def _(streams, action, websocket: WebSocket):
            for stream in streams:
                if action == "subscribe":
                    if websocket in self._active:
                        self._active[websocket].add(stream)
                    else:
                        self._active[websocket] = {stream}
                elif action == "unsubscribe":
                    self._active[websocket].remove(stream)

            if websocket in self._active and not self._active[websocket]:
                del self._active[websocket]

    async def listen(self, websocket: WebSocket):
        await websocket.accept()
        try:
            while True:
                await self.receive(websocket)
        except WebSocketDisconnect:
            self.disconnect(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self._active:
            del self._active[websocket]

    async def broadcast(self, stream: str, data: dict | BaseModel):
        await asyncio.gather(
            *[
                k.send_json(
                    {
                        "stream": stream,
                        "data": data if type(data) is dict else data.dict(),
                    }
                )
                for k, v in self._active.items()
                if stream in v
            ]
        )

    async def receive(self, websocket: WebSocket):
        msg = WebSocketMsg(**(await websocket.receive_json()))

        asyncs = []

        for func in self._on_message[msg.stream]:
            typehints = get_type_hints(func)

            kwargs = {
                **msg.data,
                **{
                    k: v(**msg.data[k])
                    for k, v in typehints.items()
                    if issubclass(v, BaseModel)
                },
                **{k: websocket for k, v in typehints.items() if v is WebSocket},
            }

            if asyncio.iscoroutinefunction(func):
                asyncs.append(func(**kwargs))
            else:
                func(**kwargs)

        await asyncio.gather(*asyncs)

    def on_message(self, stream: str):
        def decorator(func):
            if stream in self._on_message:
                self._on_message[stream].append(func)
            else:
                self._on_message[stream] = [func]

            return func

        return decorator

    def broadcast_func(self, stream: str):
        def decorator(func):
            if inspect.isgeneratorfunction(func):
                if asyncio.iscoroutinefunction(func):

                    async def wrapper(*args, **kwargs):
                        async for msg in func(*args, **kwargs):
                            await self.broadcast(stream, msg)

                else:

                    async def wrapper(*args, **kwargs):
                        for msg in func(*args, **kwargs):
                            await self.broadcast(stream, msg)

            else:
                if asyncio.iscoroutinefunction(func):

                    async def wrapper(*args, **kwargs):
                        await self.broadcast(stream, await func(*args, **kwargs))

                else:

                    async def wrapper(*args, **kwargs):
                        await self.broadcast(stream, func(*args, **kwargs))

            functools.update_wrapper(wrapper, func)

            return wrapper

        return decorator


websocket_handler = WebSocketHandler()
