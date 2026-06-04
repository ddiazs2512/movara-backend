from fastapi import WebSocket

class ConnectionManager:

    def __init__(self):
        self.connections = {}

    async def connect(
        self,
        viaje_id: int,
        websocket: WebSocket
    ):
        await websocket.accept()

        self.connections[viaje_id] = websocket

        print(
            f"WS conectado viaje={viaje_id}"
        )

    def disconnect(
        self,
        viaje_id: int
    ):
        self.connections.pop(
            viaje_id,
            None
        )

        print(
            f"WS desconectado viaje={viaje_id}"
        )

    async def enviar(
        self,
        viaje_id: int,
        data: dict
    ):
        ws = self.connections.get(viaje_id)

        if ws:
            await ws.send_json(data)

manager = ConnectionManager()
