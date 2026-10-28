from fastapi import APIRouter, Depends, Path, status
from pymongo.database import Database

from app.core.k_respuestas import k_respuestas
from app.core.k_security import k_requiere_roles
from app.database.k_conexion_mongo import k_obtener_db
from app.models.k_enums import KRol
from app.schemas.k_catalogo_schemas import KRecetaActualizar, KRecetaCrear, KRecetaSalida
from app.schemas.k_comun_schemas import KEliminacionSalida
from app.services.k_catalogo_service import KRecetaService

k_recetas_router = APIRouter(prefix="/recetas", tags=["Recetas"],
                             dependencies=[Depends(k_requiere_roles(KRol.ADMIN, KRol.COCINERO))])
K_ID = Path(alias="id", gt=0, description="id_receta")


def k_obtener_servicio(k_db: Database = Depends(k_obtener_db)) -> KRecetaService:
    return KRecetaService(k_db)


@k_recetas_router.get("", response_model=list[KRecetaSalida], summary="Listar recetas",
                      description="RF05. Cada registro es un insumo con su cantidad por unidad de producto. "
                                  "Roles: **ADMIN, COCINERO**.", responses=k_respuestas(401, 403))
def k_listar_recetas(k_servicio: KRecetaService = Depends(k_obtener_servicio)):
    return k_servicio.k_listar()


@k_recetas_router.get("/{id}", response_model=KRecetaSalida, summary="Consultar registro de receta",
                      description="Roles: **ADMIN, COCINERO**.", responses=k_respuestas(401, 403, 404))
def k_obtener_receta(k_id: int = K_ID, k_servicio: KRecetaService = Depends(k_obtener_servicio)):
    return k_servicio.k_obtener(k_id)


@k_recetas_router.post("", response_model=KRecetaSalida, status_code=status.HTTP_201_CREATED,
                       summary="Agregar insumo a la receta",
                       description="Un insumo no puede repetirse en la receta del mismo producto. "
                                   "Roles: **ADMIN, COCINERO**.", responses=k_respuestas(401, 403, 404, 409))
def k_crear_receta(k_datos: KRecetaCrear, k_servicio: KRecetaService = Depends(k_obtener_servicio)):
    return k_servicio.k_crear(k_datos)


@k_recetas_router.put("/{id}", response_model=KRecetaSalida, summary="Actualizar registro de receta",
                      description="Cambia el insumo o la cantidad. Roles: **ADMIN, COCINERO**.",
                      responses=k_respuestas(401, 403, 404, 409))
def k_actualizar_receta(k_datos: KRecetaActualizar, k_id: int = K_ID,
                        k_servicio: KRecetaService = Depends(k_obtener_servicio)):
    return k_servicio.k_actualizar(k_id, k_datos)


@k_recetas_router.delete("/{id}", response_model=KEliminacionSalida, summary="Quitar insumo de la receta",
                         description="Roles: **ADMIN, COCINERO**.", responses=k_respuestas(401, 403, 404))
def k_eliminar_receta(k_id: int = K_ID, k_servicio: KRecetaService = Depends(k_obtener_servicio)):
    return k_servicio.k_eliminar(k_id)
