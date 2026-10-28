from datetime import date

from fastapi import APIRouter, Depends, Query
from pymongo.database import Database

from app.core.k_respuestas import k_respuestas
from app.core.k_security import k_requiere_roles
from app.database.k_conexion_mongo import k_obtener_db
from app.models.k_enums import KRol
from app.schemas.k_pedido_schemas import KProductoMasVendidoSalida, KReporteVentasSalida
from app.services.k_pedido_service import KReporteService

k_reportes_router = APIRouter(prefix="/reportes", tags=["Reportes"],
                              dependencies=[Depends(k_requiere_roles(KRol.ADMIN))])


def k_obtener_servicio(k_db: Database = Depends(k_obtener_db)) -> KReporteService:
    return KReporteService(k_db)


@k_reportes_router.get("/ventas", response_model=KReporteVentasSalida, summary="Reporte de ventas",
                       description="RF11. Total vendido y número de pedidos ENTREGADOS entre dos fechas "
                                   "(incluidas). Rol: **ADMIN**.", responses=k_respuestas(400, 401, 403))
def k_reporte_ventas(k_desde: date = Query(alias="desde", examples=["2026-01-01"]),
                     k_hasta: date = Query(alias="hasta", examples=["2026-12-31"]),
                     k_servicio: KReporteService = Depends(k_obtener_servicio)):
    return k_servicio.k_ventas(k_desde, k_hasta)


@k_reportes_router.get("/productos-mas-vendidos", response_model=list[KProductoMasVendidoSalida],
                       summary="Productos más vendidos",
                       description="RF11. Ranking por cantidad vendida en pedidos ENTREGADOS. Rol: **ADMIN**.",
                       responses=k_respuestas(401, 403))
def k_productos_mas_vendidos(k_limite: int = Query(10, alias="limite", ge=1, le=100),
                             k_servicio: KReporteService = Depends(k_obtener_servicio)):
    return k_servicio.k_productos_mas_vendidos(k_limite)
