from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

from websocket_manager import manager

router = APIRouter()

@router.websocket("/ws/viaje/{viaje_id}")

async def websocket_viaje(
    websocket: WebSocket,
    viaje_id: int
):

    await manager.connect(
        viaje_id,
        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        manager.disconnect(
            viaje_id
        )

@router.get("/ws-test/{viaje_id}")

async def ws_test(
    viaje_id: int
):

    await manager.enviar(
        viaje_id,
        {
            "evento": "prueba"
        }
    )

    return {
        "ok": True
    }
