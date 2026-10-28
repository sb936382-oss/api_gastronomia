from fastapi import APIRouter, Depends, Path, status
from pymongo.database import Database

from app.core.k_respuestas import k_respuestas
from app.core.k_security import k_requiere_roles, k_usuario_actual
from app.database.k_conexion_mongo import k_obtener_db
from app.models.k_enums import KRol
from app.schemas.k_catalogo_schemas import (
    KCostoProductoSalida, KProductoActualizar, KProductoCrear, KProductoSalida, KRecetaProductoSalida,
)
from app.schemas.k_comun_schemas import KEliminacionSalida
from app.services.k_catalogo_service import KProductoService

k_productos_router = APIRouter(prefix="/productos", tags=["Productos"])
k_solo_admin = [Depends(k_requiere_roles(KRol.ADMIN))]
k_admin_cocinero = [Depends(k_requiere_roles(KRol.ADMIN, KRol.COCINERO))]
k_todos = [Depends(k_usuario_actual)]
K_ID = Path(alias="id", gt=0, description="id_producto")


def k_obtener_servicio(k_db: Database = Depends(k_obtener_db)) -> KProductoService:
    return KProductoService(k_db)


@k_productos_router.get("", response_model=list[KProductoSalida], summary="Listar productos",
                        description="RF04. Roles: todos.", responses=k_respuestas(401), dependencies=k_todos)
def k_listar_productos(k_servicio: KProductoService = Depends(k_obtener_servicio)):
    return k_servicio.k_listar()


@k_productos_router.get("/categoria/{id_categoria}", response_model=list[KProductoSalida],
                        summary="Productos de una categoría", description="Roles: todos.",
                        responses=k_respuestas(401, 404), dependencies=k_todos)
def k_listar_productos_categoria(k_id_categoria: int = Path(alias="id_categoria", gt=0),
                                 k_servicio: KProductoService = Depends(k_obtener_servicio)):
    return k_servicio.k_listar_por_categoria(k_id_categoria)


@k_productos_router.get("/{id}", response_model=KProductoSalida, summary="Consultar producto",
                        description="Roles: todos.", responses=k_respuestas(401, 404), dependencies=k_todos)
def k_obtener_producto(k_id: int = K_ID, k_servicio: KProductoService = Depends(k_obtener_servicio)):
    return k_servicio.k_obtener(k_id)


@k_productos_router.get("/{id}/receta", response_model=KRecetaProductoSalida, summary="Receta de un producto",
                        description="RF05. Insumos y cantidades de la ficha técnica. Roles: **ADMIN, COCINERO**.",
                        responses=k_respuestas(401, 403, 404), dependencies=k_admin_cocinero)
def k_receta_producto(k_id: int = K_ID, k_servicio: KProductoService = Depends(k_obtener_servicio)):
    return k_servicio.k_obtener_receta(k_id)


@k_productos_router.get("/{id}/costo", response_model=KCostoProductoSalida, summary="Costo de producción",
                        description="RF06. Costo = Σ (cantidad × costo_unitario) de la receta y margen frente al "
                                    "precio de venta. Roles: **ADMIN, COCINERO**.",
                        responses=k_respuestas(401, 403, 404), dependencies=k_admin_cocinero)
def k_costo_producto(k_id: int = K_ID, k_servicio: KProductoService = Depends(k_obtener_servicio)):
    return k_servicio.k_calcular_costo(k_id)


@k_productos_router.post("", response_model=KProductoSalida, status_code=status.HTTP_201_CREATED,
                         summary="Crear producto", description="Rol: **ADMIN**.",
                         responses=k_respuestas(401, 403, 404, 409), dependencies=k_solo_admin)
def k_crear_producto(k_datos: KProductoCrear, k_servicio: KProductoService = Depends(k_obtener_servicio)):
    return k_servicio.k_crear(k_datos)


@k_productos_router.put("/{id}", response_model=KProductoSalida, summary="Actualizar producto",
                        description="Rol: **ADMIN**.", responses=k_respuestas(401, 403, 404, 409),
                        dependencies=k_solo_admin)
def k_actualizar_producto(k_datos: KProductoActualizar, k_id: int = K_ID,
                          k_servicio: KProductoService = Depends(k_obtener_servicio)):
    return k_servicio.k_actualizar(k_id, k_datos)


@k_productos_router.delete("/{id}", response_model=KEliminacionSalida, summary="Eliminar producto",
                           description="RN04: si tiene pedidos asociados se cambia a INACTIVO. Rol: **ADMIN**.",
                           responses=k_respuestas(401, 403, 404), dependencies=k_solo_admin)
def k_eliminar_producto(k_id: int = K_ID, k_servicio: KProductoService = Depends(k_obtener_servicio)):
    return k_servicio.k_eliminar(k_id)
