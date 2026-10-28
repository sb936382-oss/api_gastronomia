from fastapi import APIRouter, Depends, Path, status
from pymongo.database import Database

from app.core.k_respuestas import k_respuestas
from app.core.k_security import k_requiere_roles, k_usuario_actual
from app.database.k_conexion_mongo import k_obtener_db
from app.models.k_enums import KRol
from app.schemas.k_catalogo_schemas import KCategoriaActualizar, KCategoriaCrear, KCategoriaSalida
from app.schemas.k_comun_schemas import KEliminacionSalida
from app.services.k_catalogo_service import KCategoriaService

k_categorias_router = APIRouter(prefix="/categorias", tags=["Categorías"])
k_solo_admin = [Depends(k_requiere_roles(KRol.ADMIN))]
k_todos = [Depends(k_usuario_actual)]
K_ID = Path(alias="id", gt=0, description="id_categoria")


def k_obtener_servicio(k_db: Database = Depends(k_obtener_db)) -> KCategoriaService:
    return KCategoriaService(k_db)


@k_categorias_router.get("", response_model=list[KCategoriaSalida], summary="Listar categorías",
                         description="RF03. Roles: todos.", responses=k_respuestas(401), dependencies=k_todos)
def k_listar_categorias(k_servicio: KCategoriaService = Depends(k_obtener_servicio)):
    return k_servicio.k_listar()


@k_categorias_router.get("/{id}", response_model=KCategoriaSalida, summary="Consultar categoría",
                         description="Roles: todos.", responses=k_respuestas(401, 404), dependencies=k_todos)
def k_obtener_categoria(k_id: int = K_ID, k_servicio: KCategoriaService = Depends(k_obtener_servicio)):
    return k_servicio.k_obtener(k_id)


@k_categorias_router.post("", response_model=KCategoriaSalida, status_code=status.HTTP_201_CREATED,
                          summary="Crear categoría", description="Rol: **ADMIN**.",
                          responses=k_respuestas(401, 403, 409), dependencies=k_solo_admin)
def k_crear_categoria(k_datos: KCategoriaCrear, k_servicio: KCategoriaService = Depends(k_obtener_servicio)):
    return k_servicio.k_crear(k_datos)


@k_categorias_router.put("/{id}", response_model=KCategoriaSalida, summary="Actualizar categoría",
                         description="Rol: **ADMIN**.", responses=k_respuestas(401, 403, 404, 409),
                         dependencies=k_solo_admin)
def k_actualizar_categoria(k_datos: KCategoriaActualizar, k_id: int = K_ID,
                           k_servicio: KCategoriaService = Depends(k_obtener_servicio)):
    return k_servicio.k_actualizar(k_id, k_datos)


@k_categorias_router.delete("/{id}", response_model=KEliminacionSalida, summary="Eliminar categoría",
                            description="Si tiene productos asociados se cambia a INACTIVO. Rol: **ADMIN**.",
                            responses=k_respuestas(401, 403, 404), dependencies=k_solo_admin)
def k_eliminar_categoria(k_id: int = K_ID, k_servicio: KCategoriaService = Depends(k_obtener_servicio)):
    return k_servicio.k_eliminar(k_id)
