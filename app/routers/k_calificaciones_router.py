from fastapi import APIRouter, Depends, Path, status
from pymongo.database import Database

from app.core.k_respuestas import k_respuestas
from app.core.k_security import k_requiere_roles
from app.database.k_conexion_mongo import k_obtener_db
from app.models.k_enums import KRol
from app.schemas.k_calificacion_schemas import (
    KCalificacionActualizar, KCalificacionCrear, KCalificacionesProductoSalida, KCalificacionSalida,
)
from app.schemas.k_comun_schemas import KEliminacionSalida
from app.services.k_calificacion_service import KCalificacionService

k_calificaciones_router = APIRouter(prefix="/calificaciones", tags=["Calificaciones"],
                                    dependencies=[Depends(k_requiere_roles(KRol.ADMIN, KRol.CAJERO))])
K_ID = Path(alias="id", description="ObjectId de MongoDB")


def k_obtener_servicio(k_db: Database = Depends(k_obtener_db)) -> KCalificacionService:
    return KCalificacionService(k_db)


@k_calificaciones_router.get("", response_model=list[KCalificacionSalida], summary="Listar calificaciones",
                             description="RF12. Documentos de la colección calificaciones. "
                                         "Roles: **ADMIN, CAJERO**.", responses=k_respuestas(401, 403))
def k_listar_calificaciones(k_servicio: KCalificacionService = Depends(k_obtener_servicio)):
    return k_servicio.k_listar()


@k_calificaciones_router.get("/producto/{id_producto}", response_model=KCalificacionesProductoSalida,
                             summary="Calificaciones y promedio de un producto",
                             description="Usa el framework de agregación de MongoDB ($unwind, $group, $avg). "
                                         "Roles: **ADMIN, CAJERO**.", responses=k_respuestas(401, 403, 404))
def k_calificaciones_producto(k_id_producto: int = Path(alias="id_producto", gt=0),
                              k_servicio: KCalificacionService = Depends(k_obtener_servicio)):
    return k_servicio.k_de_producto(k_id_producto)


@k_calificaciones_router.get("/{id}", response_model=KCalificacionSalida, summary="Consultar calificación",
                             description="Roles: **ADMIN, CAJERO**.", responses=k_respuestas(401, 403, 404))
def k_obtener_calificacion(k_id: str = K_ID, k_servicio: KCalificacionService = Depends(k_obtener_servicio)):
    return k_servicio.k_obtener(k_id)


@k_calificaciones_router.post("", response_model=KCalificacionSalida, status_code=status.HTTP_201_CREATED,
                              summary="Registrar calificación",
                              description="El pedido debe existir, pertenecer al cliente y estar "
                                          "ENTREGADO; los productos deben hacer parte del pedido. Una calificación "
                                          "por pedido. Roles: **ADMIN, CAJERO**.",
                              responses=k_respuestas(400, 401, 403, 404, 409))
def k_crear_calificacion(k_datos: KCalificacionCrear, k_servicio: KCalificacionService = Depends(k_obtener_servicio)):
    return k_servicio.k_crear(k_datos)


@k_calificaciones_router.put("/{id}", response_model=KCalificacionSalida, summary="Actualizar calificación",
                             description="Roles: **ADMIN, CAJERO**.", responses=k_respuestas(400, 401, 403, 404))
def k_actualizar_calificacion(k_datos: KCalificacionActualizar, k_id: str = K_ID,
                              k_servicio: KCalificacionService = Depends(k_obtener_servicio)):
    return k_servicio.k_actualizar(k_id, k_datos)


@k_calificaciones_router.delete("/{id}", response_model=KEliminacionSalida, summary="Eliminar calificación",
                                description="Roles: **ADMIN, CAJERO**.", responses=k_respuestas(401, 403, 404))
def k_eliminar_calificacion(k_id: str = K_ID, k_servicio: KCalificacionService = Depends(k_obtener_servicio)):
    return k_servicio.k_eliminar(k_id)
