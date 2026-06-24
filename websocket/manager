
from collections import defaultdict
from fastapi import WebSocket
from typing import Dict, Set
import asyncio

class WebSocketManager:

    def __init__(self):

        self.mercado: Set[WebSocket] = set()

        self.mis_viajes: Dict[int, Set[WebSocket]] = defaultdict(set)

        self.lock = asyncio.Lock()

    # -------------------------
    # MERCADO
    # -------------------------

    async def connect_mercado(self, websocket: WebSocket):
        await websocket.accept()

        async with self.lock:
            self.mercado.add(websocket)

    async def disconnect_mercado(self, websocket: WebSocket):

        async with self.lock:
            self.mercado.discard(websocket)

    async def notify_mercado(self):

        mensaje = {
            "type": "mercado_actualizado"
        }

        eliminar = []

        for ws in self.mercado:

            try:
                await ws.send_json(mensaje)

            except Exception:
                eliminar.append(ws)

        async with self.lock:
            for ws in eliminar:
                self.mercado.discard(ws)

    # -------------------------
    # MIS VIAJES
    # -------------------------

    async def connect_mis_viajes(
        self,
        usuario_id: int,
        websocket: WebSocket
    ):

        await websocket.accept()

        async with self.lock:
            self.mis_viajes[usuario_id].add(websocket)

    async def disconnect_mis_viajes(
        self,
        usuario_id: int,
        websocket: WebSocket
    ):

        async with self.lock:

            self.mis_viajes[usuario_id].discard(websocket)

            if not self.mis_viajes[usuario_id]:
                del self.mis_viajes[usuario_id]

    async def notify_mis_viajes(
        self,
        usuario_id: int
    ):

        mensaje = {
            "type": "mis_viajes_actualizados"
        }

        sockets = self.mis_viajes.get(usuario_id, set())

        eliminar = []

        for ws in sockets:

            try:
                await ws.send_json(mensaje)

            except Exception:
                eliminar.append(ws)

        async with self.lock:

            for ws in eliminar:
                self.mis_viajes[usuario_id].discard(ws)


manager = WebSocketManager()
