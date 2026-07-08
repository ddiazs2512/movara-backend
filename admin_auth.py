from datetime import datetime, timedelta

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import HTTPException

import os


# ======================
# CONFIG
# ======================

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise Exception("SECRET_KEY no definida")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 1440


# ======================
# PASSWORD HASH
# ======================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# ======================
# JWT ADMIN
# ======================

def create_admin_token(data: dict):

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({
        "exp": expire,
        "type": "admin"
    })

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verify_admin_token(token: str):

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "admin":
            raise HTTPException(
                status_code=401,
                detail="Token inválido"
            )

        return payload

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado"
        )
