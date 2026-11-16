from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from auth import authenticate, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


class Credenciales(BaseModel):
    username: str
    password: str


@router.post("/login", summary="Iniciar sesión")
def login(credenciales: Credenciales):
    user = authenticate(credenciales.username, credenciales.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
        )

    access_token, expires_at = create_access_token(user["username"])
    return {
        "accessToken": access_token,
        "expiresAt": expires_at,
        "user": user,
    }
