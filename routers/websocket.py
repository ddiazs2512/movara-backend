from fastapi import APIRouter
from fastapi import WebSocket
from fastapi import WebSocketDisconnect

router = APIRouter()

@router.websocket("/ws/test")

async def websocket_test(
    websocket: WebSocket
):

    await websocket.accept()

    print("WS conectado")

    try:

        while True:

            data = await websocket.receive_text()

            print(
                f"WS recibe: {data}"
            )

            await websocket.send_text(
                f"echo: {data}"
            )

    except WebSocketDisconnect:

        print(
            "WS desconectado"
        )