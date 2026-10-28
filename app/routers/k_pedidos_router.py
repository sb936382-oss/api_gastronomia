from fastapi import APIRouter, Depends, Path, status
from pymongo.database import Database

from app.core.k_respuestas import k_respuestas
from app.core.k_security import k_requiere_roles
from app.database.k_conexion_mongo import k_obtener_db
from app.models.k_enums import KEstadoPedido, KRol
from app.schemas.k_comun_schemas import KEliminacionSalida
from app.schemas.k_pedido_schemas import KPedidoActualizar, KPedidoCrear, KPedidoEstadoEntrada, KPedidoSalida
from app.services.k_pedido_service import KPedidoService

k_pedidos_router = APIRouter(prefix="/pedidos", tags=["Pedidos"])
k_admin_cajero = k_requiere_roles(KRol.ADMIN, KRol.CAJERO)
k_cambio_estado = k_requiere_roles(KRol.ADMIN, KRol.CAJERO, KRol.COCINERO)
K_ID = Path(alias="id", gt=0, description="id_pedido")


def k_obtener_servicio(k_db: Database = Depends(k_obtener_db)) -> KPedidoService:
    return KPedidoService(k_db)


@k_pedidos_router.get("", response_model=list[KPedidoSalida], summary="Listar pedidos",
                      description="RF10. Roles: **ADMIN, CAJERO**.", responses=k_respuestas(401, 403),
                      dependencies=[Depends(k_admin_cajero)])
def k_listar_pedidos(k_servicio: KPedidoService = Depends(k_obtener_servicio)):
    return k_servicio.k_listar()


@k_pedidos_router.get("/estado/{estado}", response_model=list[KPedidoSalida], summary="Pedidos por estado",
                      description="Filtra por PENDIENTE, EN_PREPARACION, ENTREGADO o ANULADO. El COCINERO lo usa "
                                  "para ver los pedidos por preparar. Roles: **ADMIN, CAJERO, COCINERO**.",
                      responses=k_respuestas(401, 403), dependencies=[Depends(k_cambio_estado)])
def k_pedidos_por_estado(k_estado: KEstadoPedido = Path(alias="estado"),
                         k_servicio: KPedidoService = Depends(k_obtener_servicio)):
    return k_servicio.k_listar_por_estado(k_estado)


@k_pedidos_router.get("/{id}", response_model=KPedidoSalida, summary="Consultar pedido",
                      description="Roles: **ADMIN, CAJERO**.", responses=k_respuestas(401, 403, 404),
                      dependencies=[Depends(k_admin_cajero)])
def k_obtener_pedido(k_id: int = K_ID, k_servicio: KPedidoService = Depends(k_obtener_servicio)):
    return k_servicio.k_obtener(k_id)


@k_pedidos_router.post("", response_model=KPedidoSalida, status_code=status.HTTP_201_CREATED,
                       summary="Registrar pedido",
                       description="RN01: se envían solo producto y cantidad; la API toma el precio actual de "
                                   "cada producto y calcula subtotales y total. Roles: **ADMIN, CAJERO**.",
                       responses=k_respuestas(400, 401, 403, 404, 409))
def k_crear_pedido(k_datos: KPedidoCrear, k_usuario: dict = Depends(k_admin_cajero),
                   k_servicio: KPedidoService = Depends(k_obtener_servicio)):
    return k_servicio.k_crear(k_datos, k_usuario)


@k_pedidos_router.put("/{id}", response_model=KPedidoSalida, summary="Actualizar pedido",
                      description="Si se envía `detalle` se reemplaza y se recalcula el total (RN01). "
                                  "RN05: un pedido ENTREGADO o ANULADO no puede modificarse (409). "
                                  "Roles: **ADMIN, CAJERO**.", responses=k_respuestas(400, 401, 403, 404, 409),
                      dependencies=[Depends(k_admin_cajero)])
def k_actualizar_pedido(k_datos: KPedidoActualizar, k_id: int = K_ID,
                        k_servicio: KPedidoService = Depends(k_obtener_servicio)):
    return k_servicio.k_actualizar(k_id, k_datos)


@k_pedidos_router.patch("/{id}/estado", response_model=KPedidoSalida, summary="Cambiar estado del pedido",
                        description="RN03: al pasar a ENTREGADO se descuentan los insumos según la receta de cada "
                                    "producto; si no hay existencias responde 409. RN05: no se puede cambiar un "
                                    "pedido ENTREGADO o ANULADO. Roles: **ADMIN, CAJERO, COCINERO**.",
                        responses=k_respuestas(400, 401, 403, 404, 409), dependencies=[Depends(k_cambio_estado)])
def k_cambiar_estado_pedido(k_datos: KPedidoEstadoEntrada, k_id: int = K_ID,
                            k_servicio: KPedidoService = Depends(k_obtener_servicio)):
    return k_servicio.k_cambiar_estado(k_id, k_datos.estado)


@k_pedidos_router.delete("/{id}", response_model=KEliminacionSalida, summary="Anular pedido",
                         description="Borrado lógico: el pedido pasa a ANULADO para conservar el historial. "
                                     "RN05: 409 si ya está ENTREGADO o ANULADO. Roles: **ADMIN, CAJERO**.",
                         responses=k_respuestas(401, 403, 404, 409), dependencies=[Depends(k_admin_cajero)])
def k_anular_pedido(k_id: int = K_ID, k_servicio: KPedidoService = Depends(k_obtener_servicio)):
    return k_servicio.k_anular(k_id)
