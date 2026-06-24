from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websocket.manager import manager

router = APIRouter()

@router.websocket("/ws/mercado")
async def websocket_mercado(websocket: WebSocket):

    await manager.connect_mercado(websocket)

    try:

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:

        await manager.disconnect_mercado(websocket)
