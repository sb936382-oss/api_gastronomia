from fastapi import APIRouter, Depends, Path, status
from pymongo.database import Database

from app.core.k_respuestas import k_respuestas
from app.core.k_security import k_requiere_roles
from app.database.k_conexion_mongo import k_obtener_db
from app.models.k_enums import KRol
from app.schemas.k_comun_schemas import KEliminacionSalida
from app.schemas.k_usuario_schemas import KUsuarioActualizar, KUsuarioCrear, KUsuarioSalida
from app.services.k_usuario_service import KUsuarioService

k_solo_admin = k_requiere_roles(KRol.ADMIN)
k_usuarios_router = APIRouter(prefix="/usuarios", tags=["Usuarios"], dependencies=[Depends(k_solo_admin)])
K_ID = Path(alias="id", gt=0, description="id_usuario")


def k_obtener_servicio(k_db: Database = Depends(k_obtener_db)) -> KUsuarioService:
    return KUsuarioService(k_db)


@k_usuarios_router.get("", response_model=list[KUsuarioSalida], summary="Listar usuarios",
                       description="RF02. Lista los usuarios (sin contraseña, RN06). Rol: **ADMIN**.",
                       responses=k_respuestas(401, 403))
def k_listar_usuarios(k_servicio: KUsuarioService = Depends(k_obtener_servicio)):
    return k_servicio.k_listar()


@k_usuarios_router.get("/{id}", response_model=KUsuarioSalida, summary="Consultar usuario",
                       description="Rol: **ADMIN**.", responses=k_respuestas(401, 403, 404))
def k_obtener_usuario(k_id: int = K_ID, k_servicio: KUsuarioService = Depends(k_obtener_servicio)):
    return k_servicio.k_obtener(k_id)


@k_usuarios_router.post("", response_model=KUsuarioSalida, status_code=status.HTTP_201_CREATED,
                        summary="Crear usuario",
                        description="Crea un usuario con rol ADMIN, CAJERO o COCINERO. Rol: **ADMIN**.",
                        responses=k_respuestas(401, 403, 409))
def k_crear_usuario(k_datos: KUsuarioCrear, k_servicio: KUsuarioService = Depends(k_obtener_servicio)):
    return k_servicio.k_crear(k_datos)


@k_usuarios_router.put("/{id}", response_model=KUsuarioSalida, summary="Actualizar usuario",
                       description="Actualiza solo los campos enviados. Rol: **ADMIN**.",
                       responses=k_respuestas(401, 403, 404, 409))
def k_actualizar_usuario(k_datos: KUsuarioActualizar, k_id: int = K_ID,
                         k_servicio: KUsuarioService = Depends(k_obtener_servicio)):
    return k_servicio.k_actualizar(k_id, k_datos)


@k_usuarios_router.delete("/{id}", response_model=KEliminacionSalida, summary="Eliminar usuario",
                          description="Si el usuario registró pedidos o compras se cambia a INACTIVO. "
                                      "Rol: **ADMIN**.",
                          responses=k_respuestas(401, 403, 404, 409))
def k_eliminar_usuario(k_id: int = K_ID, k_usuario_sesion: dict = Depends(k_solo_admin),
                       k_servicio: KUsuarioService = Depends(k_obtener_servicio)):
    return k_servicio.k_eliminar(k_id, k_usuario_sesion)
