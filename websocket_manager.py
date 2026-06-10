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

        if viaje_id not in self.connections:
            self.connections[viaje_id] = set()

        self.connections[viaje_id].add(websocket)

        print(
            f"WS conectado viaje={viaje_id}"
        )

    def disconnect(
        self,
        viaje_id: int,
        websocket: WebSocket
    ):

        conexiones = self.connections.get(viaje_id)

        if not conexiones:
            return

        conexiones.discard(websocket)

        if not conexiones:
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

        conexiones = self.connections.get(viaje_id)

        if not conexiones:

            print(
                f"WS no conectado viaje={viaje_id}"
            )

            return False

        desconectados = []

        for ws in conexiones:

            try:

                await ws.send_json(data)

            except Exception as e:

                print(
                    f"WS error viaje={viaje_id}: {e}"
                )

                desconectados.append(ws)

        for ws in desconectados:
            conexiones.discard(ws)

        return True


manager = ConnectionManager()
