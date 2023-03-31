import asyncio
from os import environ as env


from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

import api.utils as utils
import api.routers as routers


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(utils.data.file_watcher())

    yield

    utils.data.file_watcher.stop()


app = FastAPI(lifespan=lifespan)

if env["API_ENV"] == "development":
    app.add_middleware(CORSMiddleware, allow_origins=["*"])
app.include_router(routers.graph)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await utils.websocket.websocket_handler(websocket)
