import uuid
from datetime import datetime, timedelta


class SessionTokenService:

    def __init__(self):
        self._sessions = {}

    def crear(self):

        session_id = str(uuid.uuid4())
        google_token = str(uuid.uuid4())

        self._sessions[session_id] = {
            "google_token": google_token,
            "created_at": datetime.utcnow()
        }

        return session_id

    def obtener_google_token(self, session_id: str):

        session = self._sessions.get(session_id)

        if not session:
            return None

        return session["google_token"]

    def eliminar(self, session_id: str):

        self._sessions.pop(session_id, None)

    def limpiar_expiradas(self):

        ahora = datetime.utcnow()

        expiradas = []

        for session_id, session in self._sessions.items():

            if ahora - session["created_at"] > timedelta(minutes=5):
                expiradas.append(session_id)

        for session_id in expiradas:
            self.eliminar(session_id)


session_token_service = SessionTokenService()
