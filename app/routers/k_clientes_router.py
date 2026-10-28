from fastapi import APIRouter, Depends, Path, status
from pymongo.database import Database

from app.core.k_respuestas import k_respuestas
from app.core.k_security import k_requiere_roles
from app.database.k_conexion_mongo import k_obtener_db
from app.models.k_enums import KRol
from app.schemas.k_comun_schemas import KEliminacionSalida
from app.schemas.k_pedido_schemas import KClienteActualizar, KClienteCrear, KClienteSalida, KPedidoSalida
from app.services.k_pedido_service import KClienteService

k_clientes_router = APIRouter(prefix="/clientes", tags=["Clientes"],
                              dependencies=[Depends(k_requiere_roles(KRol.ADMIN, KRol.CAJERO))])
K_ID = Path(alias="id", gt=0, description="id_cliente")


def k_obtener_servicio(k_db: Database = Depends(k_obtener_db)) -> KClienteService:
    return KClienteService(k_db)


@k_clientes_router.get("", response_model=list[KClienteSalida], summary="Listar clientes",
                       description="RF09. Roles: **ADMIN, CAJERO**.", responses=k_respuestas(401, 403))
def k_listar_clientes(k_servicio: KClienteService = Depends(k_obtener_servicio)):
    return k_servicio.k_listar()


@k_clientes_router.get("/{id}", response_model=KClienteSalida, summary="Consultar cliente",
                       description="Roles: **ADMIN, CAJERO**.", responses=k_respuestas(401, 403, 404))
def k_obtener_cliente(k_id: int = K_ID, k_servicio: KClienteService = Depends(k_obtener_servicio)):
    return k_servicio.k_obtener(k_id)


@k_clientes_router.get("/{id}/pedidos", response_model=list[KPedidoSalida],
                       summary="Historial de pedidos de un cliente", description="Roles: **ADMIN, CAJERO**.",
                       responses=k_respuestas(401, 403, 404))
def k_pedidos_cliente(k_id: int = K_ID, k_servicio: KClienteService = Depends(k_obtener_servicio)):
    return k_servicio.k_listar_pedidos(k_id)


@k_clientes_router.post("", response_model=KClienteSalida, status_code=status.HTTP_201_CREATED,
                        summary="Crear cliente",
                        description="tipo_cliente: APRENDIZ, INSTRUCTOR, FUNCIONARIO o EXTERNO. "
                                    "Roles: **ADMIN, CAJERO**.", responses=k_respuestas(401, 403, 409))
def k_crear_cliente(k_datos: KClienteCrear, k_servicio: KClienteService = Depends(k_obtener_servicio)):
    return k_servicio.k_crear(k_datos)


@k_clientes_router.put("/{id}", response_model=KClienteSalida, summary="Actualizar cliente",
                       description="Roles: **ADMIN, CAJERO**.", responses=k_respuestas(401, 403, 404, 409))
def k_actualizar_cliente(k_datos: KClienteActualizar, k_id: int = K_ID,
                         k_servicio: KClienteService = Depends(k_obtener_servicio)):
    return k_servicio.k_actualizar(k_id, k_datos)


@k_clientes_router.delete("/{id}", response_model=KEliminacionSalida, summary="Eliminar cliente",
                          description="RN04: si tiene pedidos se cambia a INACTIVO. Roles: **ADMIN, CAJERO**.",
                          responses=k_respuestas(401, 403, 404))
def k_eliminar_cliente(k_id: int = K_ID, k_servicio: KClienteService = Depends(k_obtener_servicio)):
    return k_servicio.k_eliminar(k_id)
