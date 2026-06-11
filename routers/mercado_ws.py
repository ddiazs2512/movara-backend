from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

router = APIRouter()

clientes = set()

@router.websocket("/ws/mercado")
async def websocket_mercado(
    websocket: WebSocket
):

    await websocket.accept()

    clientes.add(websocket)

    try:

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:

        clientes.discard(websocket)


async def broadcast_refresh():

    muertos = []

    for ws in clientes:

        try:

            await ws.send_json({
                "tipo": "refresh"
            })

        except:

            muertos.append(ws)

    for ws in muertos:
        clientes.discard(ws)
