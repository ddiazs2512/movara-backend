from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from websocket.manager import manager

router = APIRouter()

@router.websocket("/ws/mis-viajes/{usuario_id}")
async def websocket_mis_viajes(
    websocket: WebSocket,
    usuario_id: int
):

    await manager.connect_mis_viajes(
        usuario_id,
        websocket
    )

    try:

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:

        await manager.disconnect_mis_viajes(
            usuario_id,
            websocket
        )
