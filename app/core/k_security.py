from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pymongo.database import Database

from app.core.k_config import k_config
from app.database.k_conexion_mongo import k_obtener_db
from app.models.k_enums import KEstado, KRol

k_esquema_bearer = HTTPBearer(auto_error=False, description="Token JWT obtenido en POST /api/v1/auth/login")


def k_cifrar_password(k_password: str) -> str:
    """RN06: las contraseñas se guardan cifradas con bcrypt."""
    return bcrypt.hashpw(k_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def k_verificar_password(k_password: str, k_hash: str) -> bool:
    try:
        return bcrypt.checkpw(k_password.encode("utf-8"), k_hash.encode("utf-8"))
    except ValueError:
        return False


def k_crear_token(k_usuario: dict) -> str:
    k_ahora_utc = datetime.now(timezone.utc)
    k_payload = {
        "sub": str(k_usuario["id_usuario"]),
        "rol": k_usuario["rol"],
        "iat": k_ahora_utc,
        "exp": k_ahora_utc + timedelta(minutes=k_config.k_jwt_expire_minutes),
    }
    return jwt.encode(k_payload, k_config.k_jwt_secret, algorithm=k_config.k_jwt_algorithm)


def k_error_401(k_mensaje: str) -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, k_mensaje, headers={"WWW-Authenticate": "Bearer"})


def k_usuario_actual(
    k_credenciales: HTTPAuthorizationCredentials | None = Depends(k_esquema_bearer),
    k_db: Database = Depends(k_obtener_db),
) -> dict:
    """Valida el token Bearer y retorna el usuario autenticado (401 si no hay token o es inválido)."""
    if k_credenciales is None:
        raise k_error_401("Token requerido. Envíe el encabezado Authorization: Bearer <token>")
    try:
        k_datos = jwt.decode(k_credenciales.credentials, k_config.k_jwt_secret,
                             algorithms=[k_config.k_jwt_algorithm])
    except jwt.ExpiredSignatureError:
        raise k_error_401("El token expiró, inicie sesión nuevamente")
    except jwt.PyJWTError:
        raise k_error_401("Token inválido")
    k_usuario = k_db["usuarios"].find_one({"id_usuario": int(k_datos.get("sub", 0))}, {"_id": 0})
    if k_usuario is None or k_usuario["estado"] != KEstado.ACTIVO:
        raise k_error_401("El usuario del token no existe o está INACTIVO")
    return k_usuario


def k_requiere_roles(*k_roles: KRol):
    """Dependencia que permite el acceso solo a los roles indicados (403 si el rol no tiene permiso)."""

    def k_verificar_rol(k_usuario: dict = Depends(k_usuario_actual)) -> dict:
        if k_usuario["rol"] not in k_roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN,
                                f"El rol {k_usuario['rol']} no tiene permiso para este recurso")
        return k_usuario

    return k_verificar_rol
