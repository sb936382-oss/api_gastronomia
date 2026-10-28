from fastapi import APIRouter, Depends, Path, Query, status
from pymongo.database import Database

from app.core.k_respuestas import k_respuestas
from app.core.k_security import k_requiere_roles
from app.database.k_conexion_mongo import k_obtener_db
from app.models.k_enums import KRol
from app.schemas.k_catalogo_schemas import KInsumoActualizar, KInsumoCrear, KInsumoPorVencerSalida, KInsumoSalida
from app.schemas.k_comun_schemas import KEliminacionSalida
from app.services.k_catalogo_service import KInsumoService

k_insumos_router = APIRouter(prefix="/insumos", tags=["Insumos"],
                             dependencies=[Depends(k_requiere_roles(KRol.ADMIN, KRol.COCINERO))])
K_ID = Path(alias="id", gt=0, description="id_insumo")
K_ERRORES = k_respuestas(401, 403)


def k_obtener_servicio(k_db: Database = Depends(k_obtener_db)) -> KInsumoService:
    return KInsumoService(k_db)


@k_insumos_router.get("", response_model=list[KInsumoSalida], summary="Listar insumos",
                      description="RF07. Roles: **ADMIN, COCINERO**.", responses=K_ERRORES)
def k_listar_insumos(k_servicio: KInsumoService = Depends(k_obtener_servicio)):
    return k_servicio.k_listar()


@k_insumos_router.get("/stock-bajo", response_model=list[KInsumoSalida], summary="Insumos con stock bajo",
                      description="RF07. Insumos activos con stock_actual <= stock_minimo. "
                                  "Roles: **ADMIN, COCINERO**.", responses=K_ERRORES)
def k_insumos_stock_bajo(k_servicio: KInsumoService = Depends(k_obtener_servicio)):
    return k_servicio.k_stock_bajo()


@k_insumos_router.get("/por-vencer", response_model=list[KInsumoPorVencerSalida],
                      summary="Insumos próximos a vencer",
                      description="RF07. Insumos que vencen entre hoy y los próximos N días. "
                                  "Roles: **ADMIN, COCINERO**.", responses=K_ERRORES)
def k_insumos_por_vencer(k_dias: int = Query(7, alias="dias", ge=0, le=365, description="Número de días"),
                         k_servicio: KInsumoService = Depends(k_obtener_servicio)):
    return k_servicio.k_por_vencer(k_dias)


@k_insumos_router.get("/{id}", response_model=KInsumoSalida, summary="Consultar insumo",
                      description="Roles: **ADMIN, COCINERO**.", responses=k_respuestas(401, 403, 404))
def k_obtener_insumo(k_id: int = K_ID, k_servicio: KInsumoService = Depends(k_obtener_servicio)):
    return k_servicio.k_obtener(k_id)


@k_insumos_router.post("", response_model=KInsumoSalida, status_code=status.HTTP_201_CREATED,
                       summary="Crear insumo", description="Roles: **ADMIN, COCINERO**.",
                       responses=k_respuestas(401, 403, 409))
def k_crear_insumo(k_datos: KInsumoCrear, k_servicio: KInsumoService = Depends(k_obtener_servicio)):
    return k_servicio.k_crear(k_datos)


@k_insumos_router.put("/{id}", response_model=KInsumoSalida, summary="Actualizar insumo",
                      description="Roles: **ADMIN, COCINERO**.", responses=k_respuestas(401, 403, 404, 409))
def k_actualizar_insumo(k_datos: KInsumoActualizar, k_id: int = K_ID,
                        k_servicio: KInsumoService = Depends(k_obtener_servicio)):
    return k_servicio.k_actualizar(k_id, k_datos)


@k_insumos_router.delete("/{id}", response_model=KEliminacionSalida, summary="Eliminar insumo",
                         description="RN04: si tiene compras o recetas asociadas se cambia a INACTIVO. "
                                     "Roles: **ADMIN, COCINERO**.", responses=k_respuestas(401, 403, 404))
def k_eliminar_insumo(k_id: int = K_ID, k_servicio: KInsumoService = Depends(k_obtener_servicio)):
    return k_servicio.k_eliminar(k_id)
