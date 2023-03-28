import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import api.utils as utils
import api.routers as routers

file_watcher = utils.data.FileWatcher()
websocket_handler = utils.websocket.WebSocketHandler()
compute_graph = utils.graph.ComputeGraph()


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(file_watcher())

    yield

    file_watcher.stop()


app = FastAPI(lifespan=lifespan)
app.include_router(routers.graph)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_handler(websocket)
