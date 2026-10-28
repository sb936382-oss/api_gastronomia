from fastapi import APIRouter, Depends, Path, status
from pymongo.database import Database

from app.core.k_respuestas import k_respuestas
from app.core.k_security import k_requiere_roles
from app.database.k_conexion_mongo import k_obtener_db
from app.models.k_enums import KRol
from app.schemas.k_comun_schemas import KEliminacionSalida
from app.schemas.k_compra_schemas import KCompraActualizar, KCompraCrear, KCompraSalida
from app.services.k_compra_service import KCompraService

k_solo_admin = k_requiere_roles(KRol.ADMIN)
k_compras_router = APIRouter(prefix="/compras", tags=["Compras"], dependencies=[Depends(k_solo_admin)])
K_ID = Path(alias="id", gt=0, description="id_compra")


def k_obtener_servicio(k_db: Database = Depends(k_obtener_db)) -> KCompraService:
    return KCompraService(k_db)


@k_compras_router.get("", response_model=list[KCompraSalida], summary="Listar compras",
                      description="RF08. Compras con su detalle. Rol: **ADMIN**.", responses=k_respuestas(401, 403))
def k_listar_compras(k_servicio: KCompraService = Depends(k_obtener_servicio)):
    return k_servicio.k_listar()


@k_compras_router.get("/{id}", response_model=KCompraSalida, summary="Consultar compra",
                      description="Rol: **ADMIN**.", responses=k_respuestas(401, 403, 404))
def k_obtener_compra(k_id: int = K_ID, k_servicio: KCompraService = Depends(k_obtener_servicio)):
    return k_servicio.k_obtener(k_id)


@k_compras_router.post("", response_model=KCompraSalida, status_code=status.HTTP_201_CREATED,
                       summary="Registrar compra",
                       description="RN02: incrementa el stock_actual de cada insumo comprado y actualiza su "
                                   "costo_unitario. Subtotales y total los calcula la API. Rol: **ADMIN**.",
                       responses=k_respuestas(400, 401, 403, 404, 409))
def k_crear_compra(k_datos: KCompraCrear, k_usuario: dict = Depends(k_solo_admin),
                   k_servicio: KCompraService = Depends(k_obtener_servicio)):
    return k_servicio.k_crear(k_datos, k_usuario)


@k_compras_router.put("/{id}", response_model=KCompraSalida, summary="Actualizar compra",
                      description="Actualiza el encabezado. Si se envía `detalle`, revierte el inventario del "
                                  "detalle anterior y aplica el nuevo (RN02). Rol: **ADMIN**.",
                      responses=k_respuestas(400, 401, 403, 404, 409))
def k_actualizar_compra(k_datos: KCompraActualizar, k_id: int = K_ID,
                        k_servicio: KCompraService = Depends(k_obtener_servicio)):
    return k_servicio.k_actualizar(k_id, k_datos)


@k_compras_router.delete("/{id}", response_model=KEliminacionSalida, summary="Eliminar compra",
                         description="Descuenta del inventario las cantidades que ingresó la compra "
                                     "(409 si el stock quedaría negativo). Rol: **ADMIN**.",
                         responses=k_respuestas(401, 403, 404, 409))
def k_eliminar_compra(k_id: int = K_ID, k_servicio: KCompraService = Depends(k_obtener_servicio)):
    return k_servicio.k_eliminar(k_id)
