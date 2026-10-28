import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError, PyMongoError

from app.routers import (
    k_auth_router, k_calificaciones_router, k_categorias_router, k_clientes_router, k_compras_router,
    k_insumos_router, k_pedidos_router, k_productos_router, k_proveedores_router, k_recetas_router,
    k_reportes_router, k_usuarios_router,
)

k_log = logging.getLogger("api_gastronomia")

K_DESCRIPCION = """
API REST de la **Unidad Productiva de Gastronomía** — Centro de Gestión y Desarrollo Sostenible Surcolombiano (CGDSS).

* **Base de datos única: MongoDB** (`bd_gastronomia`) con las colecciones usuarios, categorias, productos,
  insumos, recetas, proveedores, compras, clientes, pedidos y calificaciones.

**Seguridad:** todos los endpoints requieren `Authorization: Bearer <token>` excepto `POST /api/v1/auth/login`.
Use el botón **Authorize** con el token obtenido en el login. Usuarios de prueba: ver README.md.

**Reglas de negocio:** RN01 totales calculados por la API · RN02 compras suben stock y costo ·
RN03 entregar descuenta insumos (409 sin existencias) · RN04 borrado lógico con movimientos ·
RN05 pedido ENTREGADO/ANULADO no se modifica · RN06 contraseñas con bcrypt, nunca se devuelven.
"""

k_app = FastAPI(title="API Gastronomía CGDSS", version="1.0.0", description=K_DESCRIPCION)

for k_router in (k_auth_router.k_auth_router, k_usuarios_router.k_usuarios_router,
                 k_categorias_router.k_categorias_router, k_productos_router.k_productos_router,
                 k_insumos_router.k_insumos_router, k_recetas_router.k_recetas_router,
                 k_proveedores_router.k_proveedores_router, k_compras_router.k_compras_router,
                 k_clientes_router.k_clientes_router, k_pedidos_router.k_pedidos_router,
                 k_reportes_router.k_reportes_router, k_calificaciones_router.k_calificaciones_router):
    k_app.include_router(k_router, prefix="/api/v1")


@k_app.exception_handler(DuplicateKeyError)
def k_error_duplicado_mongo(k_request: Request, k_error: DuplicateKeyError):
    return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                        content={"detail": "Ya existe un documento con esa llave única"})


@k_app.exception_handler(PyMongoError)
def k_error_base_datos(k_request: Request, k_error: Exception):
    k_log.exception("Error de base de datos", exc_info=k_error)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        content={"detail": "Error interno al acceder a la base de datos"})


@k_app.exception_handler(Exception)
def k_error_inesperado(k_request: Request, k_error: Exception):
    k_log.exception("Error no controlado", exc_info=k_error)
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        content={"detail": "Error interno del servidor"})
