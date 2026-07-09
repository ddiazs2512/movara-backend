import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from sqlalchemy.orm import Session


# 📍 Ruta al JSON
import os
SERVICE_ACCOUNT_FILE = os.getenv("FIREBASE_CREDENTIALS")

# 📍 ID de tu proyecto Firebase (IMPORTANTE)
PROJECT_ID = "movara-production-fb2c3"

def get_access_token():
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=["https://www.googleapis.com/auth/firebase.messaging"]
    )

    credentials.refresh(Request())
    return credentials.token


def enviar_notificacion_data(token: str, data: dict, db: Session = None):

    access_token = get_access_token()

    url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    body = {
        "message": {
            "token": token,
            "data": {k: str(v) for k, v in data.items()},
            "android": {
                "priority": "HIGH"
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=body, timeout=5)

        print("========== FCM ==========")
        print("STATUS:", response.status_code)
        print("BODY:", response.text)
        print("DATA:", data)
        print("=========================")

    except Exception as e:
        print(f"❌ ERROR FCM REQUEST: {e}")
        return

    # =========================
    # 🔴 LIMPIAR TOKEN INVÁLIDO
    # =========================
    if response.status_code in [400, 404]:

        error_text = response.text.lower()

        if any(err in error_text for err in [
            "invalid-registration-token",
            "registration-token-not-registered",
            "unregistered"
        ]):

            import logging
            logging.warning("Token inválido detectado")

            from database import SessionLocal
            from models import FCMToken

            close_db = False

            if db is None:
                db = SessionLocal()
                close_db = True

            try:
                db.query(FCMToken).filter(
                    FCMToken.token == token
                ).delete()
                db.commit()

                logging.info("Token eliminado de la base de datos")

            except Exception as e:
                logging.error(f"Error eliminando token: {e}")

            finally:
                if close_db:
                    db.close()
