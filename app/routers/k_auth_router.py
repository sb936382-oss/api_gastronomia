from fastapi import APIRouter, Depends, status
from pymongo.database import Database

from app.core.k_respuestas import k_respuestas
from app.core.k_security import k_requiere_roles, k_usuario_actual
from app.database.k_conexion_mongo import k_obtener_db
from app.models.k_enums import KRol
from app.schemas.k_usuario_schemas import KLoginEntrada, KTokenSalida, KUsuarioCrear, KUsuarioSalida
from app.services.k_usuario_service import KUsuarioService

k_auth_router = APIRouter(prefix="/auth", tags=["Autenticación"])


def k_obtener_servicio(k_db: Database = Depends(k_obtener_db)) -> KUsuarioService:
    return KUsuarioService(k_db)


@k_auth_router.post("/login", response_model=KTokenSalida, summary="Iniciar sesión",
                    description="RF01. Valida correo y contraseña y retorna un token JWT con el rol del usuario. "
                                "**Único endpoint público** de la API.",
                    responses=k_respuestas(401))
def k_login(k_datos: KLoginEntrada, k_servicio: KUsuarioService = Depends(k_obtener_servicio)):
    return k_servicio.k_login(k_datos)


@k_auth_router.post("/registro", response_model=KUsuarioSalida, status_code=status.HTTP_201_CREATED,
                    summary="Registrar usuario",
                    description="Registra un usuario del sistema con contraseña cifrada (bcrypt). Rol: **ADMIN**.",
                    responses=k_respuestas(401, 403, 409),
                    dependencies=[Depends(k_requiere_roles(KRol.ADMIN))])
def k_registrar(k_datos: KUsuarioCrear, k_servicio: KUsuarioService = Depends(k_obtener_servicio)):
    return k_servicio.k_crear(k_datos)


@k_auth_router.get("/perfil", response_model=KUsuarioSalida, summary="Perfil del usuario autenticado",
                   description="Retorna los datos del usuario dueño del token. Roles: todos.",
                   responses=k_respuestas(401))
def k_perfil(k_usuario: dict = Depends(k_usuario_actual)):
    return k_usuario
