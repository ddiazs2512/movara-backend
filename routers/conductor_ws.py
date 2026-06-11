from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

router = APIRouter()

conductores = {}

@router.websocket("/ws/conductor/{conductor_id}")
async def websocket_conductor(
    websocket: WebSocket,
    conductor_id: int
):

    await websocket.accept()

    if conductor_id not in conductores:
        conductores[conductor_id] = set()

    conductores[conductor_id].add(websocket)

    try:

        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:

        conductores[conductor_id].discard(websocket)


async def refresh_conductor(
    conductor_id: int
):

    if conductor_id not in conductores:
        return

    muertos = []

    for ws in conductores[conductor_id]:

        try:

            await ws.send_json({
                "tipo": "refresh"
            })

        except:

            muertos.append(ws)

    for ws in muertos:
        conductores[conductor_id].discard(ws)
