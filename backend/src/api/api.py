import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import api.utils as utils
import api.routers as routers

file_watcher = utils.data.FileWatcher()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start file watcher
    asyncio.create_task(file_watcher())

    yield

    file_watcher.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(routers.graph)


websocket_handler = utils.websocket.WebSocketHandler()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_handler(websocket)
