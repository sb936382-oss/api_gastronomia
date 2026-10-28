from fastapi import APIRouter, Depends, Path, status
from pymongo.database import Database

from app.core.k_respuestas import k_respuestas
from app.core.k_security import k_requiere_roles
from app.database.k_conexion_mongo import k_obtener_db
from app.models.k_enums import KRol
from app.schemas.k_comun_schemas import KEliminacionSalida
from app.schemas.k_compra_schemas import KCompraSalida, KProveedorActualizar, KProveedorCrear, KProveedorSalida
from app.services.k_compra_service import KProveedorService

k_proveedores_router = APIRouter(prefix="/proveedores", tags=["Proveedores"],
                                 dependencies=[Depends(k_requiere_roles(KRol.ADMIN))])
K_ID = Path(alias="id", gt=0, description="id_proveedor")


def k_obtener_servicio(k_db: Database = Depends(k_obtener_db)) -> KProveedorService:
    return KProveedorService(k_db)


@k_proveedores_router.get("", response_model=list[KProveedorSalida], summary="Listar proveedores",
                          description="RF08. Rol: **ADMIN**.", responses=k_respuestas(401, 403))
def k_listar_proveedores(k_servicio: KProveedorService = Depends(k_obtener_servicio)):
    return k_servicio.k_listar()


@k_proveedores_router.get("/{id}", response_model=KProveedorSalida, summary="Consultar proveedor",
                          description="Rol: **ADMIN**.", responses=k_respuestas(401, 403, 404))
def k_obtener_proveedor(k_id: int = K_ID, k_servicio: KProveedorService = Depends(k_obtener_servicio)):
    return k_servicio.k_obtener(k_id)


@k_proveedores_router.get("/{id}/compras", response_model=list[KCompraSalida],
                          summary="Historial de compras de un proveedor", description="Rol: **ADMIN**.",
                          responses=k_respuestas(401, 403, 404))
def k_compras_proveedor(k_id: int = K_ID, k_servicio: KProveedorService = Depends(k_obtener_servicio)):
    return k_servicio.k_listar_compras(k_id)


@k_proveedores_router.post("", response_model=KProveedorSalida, status_code=status.HTTP_201_CREATED,
                           summary="Crear proveedor", description="Rol: **ADMIN**.",
                           responses=k_respuestas(401, 403, 409))
def k_crear_proveedor(k_datos: KProveedorCrear, k_servicio: KProveedorService = Depends(k_obtener_servicio)):
    return k_servicio.k_crear(k_datos)


@k_proveedores_router.put("/{id}", response_model=KProveedorSalida, summary="Actualizar proveedor",
                          description="Rol: **ADMIN**.", responses=k_respuestas(401, 403, 404, 409))
def k_actualizar_proveedor(k_datos: KProveedorActualizar, k_id: int = K_ID,
                           k_servicio: KProveedorService = Depends(k_obtener_servicio)):
    return k_servicio.k_actualizar(k_id, k_datos)


@k_proveedores_router.delete("/{id}", response_model=KEliminacionSalida, summary="Eliminar proveedor",
                             description="RN04: si tiene compras se cambia a INACTIVO. Rol: **ADMIN**.",
                             responses=k_respuestas(401, 403, 404))
def k_eliminar_proveedor(k_id: int = K_ID, k_servicio: KProveedorService = Depends(k_obtener_servicio)):
    return k_servicio.k_eliminar(k_id)
