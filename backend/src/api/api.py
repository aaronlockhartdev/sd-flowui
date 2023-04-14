import asyncio
from os import environ as env


from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from . import services
from . import compute


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(services.file_watcher())
    asyncio.create_task(compute.executor())

    yield

    services.file_watcher.stop()
    compute.executor.cleanup()


app = FastAPI(lifespan=lifespan)

if env["API_ENV"] == "development":
    app.add_middleware(CORSMiddleware, allow_origins=["*"])


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await services.websocket_handler.listen(websocket)


import api.routers as routers

app.include_router(routers.graph)
app.include_router(routers.files)
