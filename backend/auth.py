import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_token_secret = os.getenv("GAMESTATS_AUTH_SECRET")
_TOKEN_SECRET = (
    _token_secret.encode("utf-8") if _token_secret else secrets.token_bytes(32)
)
_TOKEN_TTL_SECONDS = 12 * 60 * 60
_bearer = HTTPBearer(auto_error=False)

USERS = {
    "admin": {
        "password": os.getenv("GAMESTATS_ADMIN_PASSWORD", "admin123"),
        "role": "admin",
    },
    "usuario": {
        "password": os.getenv("GAMESTATS_USER_PASSWORD", "usuario123"),
        "role": "user",
    },
}


def _encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def create_access_token(username: str) -> tuple[str, int]:
    expires_at = int(time.time()) + _TOKEN_TTL_SECONDS
    payload = _encode(
        json.dumps(
            {"sub": username, "exp": expires_at}, separators=(",", ":")
        ).encode("utf-8")
    )
    signature = _encode(
        hmac.new(_TOKEN_SECRET, payload.encode("ascii"), hashlib.sha256).digest()
    )
    return f"{payload}.{signature}", expires_at


def _unauthorized() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas o sesión vencida.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer)
    ],
) -> dict[str, str]:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized()

    try:
        payload, signature = credentials.credentials.split(".", maxsplit=1)
        expected_signature = _encode(
            hmac.new(_TOKEN_SECRET, payload.encode("ascii"), hashlib.sha256).digest()
        )
        if not hmac.compare_digest(signature, expected_signature):
            raise _unauthorized()

        padded_payload = payload + "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(padded_payload))
        username = data["sub"]
        user = USERS[username]
        if not isinstance(data["exp"], int) or data["exp"] <= int(time.time()):
            raise _unauthorized()
    except HTTPException:
        raise
    except (KeyError, TypeError, ValueError, UnicodeDecodeError, json.JSONDecodeError):
        raise _unauthorized() from None

    return {"username": username, "role": user["role"]}


def require_admin(
    user: Annotated[dict[str, str], Depends(get_current_user)],
) -> dict[str, str]:
    if user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere el rol de administrador.",
        )
    return user


def authenticate(username: str, password: str) -> dict[str, str] | None:
    user = USERS.get(username)
    if user is None or not secrets.compare_digest(
        user["password"].encode("utf-8"), password.encode("utf-8")
    ):
        return None
    return {"username": username, "role": user["role"]}
