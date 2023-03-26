from fastapi import APIRouter, WebSocket, WebSocketDisconnect

import api.utils as utils
import api.routers as routers

router = APIRouter()

router.include_router(routers.graph)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await utils.websocket.handler.connect(websocket)
    try:
        while True:
            await utils.websocket.handler.receive(websocket)
    except WebSocketDisconnect:
        utils.websocket.handler.disconnect(websocket)
