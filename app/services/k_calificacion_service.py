from fastapi import HTTPException, status
from pymongo.database import Database

from app.core.k_config import k_ahora
from app.models.k_enums import KEstadoPedido
from app.repositories.k_base_repository import KRepositorioBase
from app.repositories.k_calificacion_repository import KCalificacionRepository
from app.schemas.k_calificacion_schemas import (
    KCalificacionActualizar, KCalificacionCrear, KCalificacionesProductoSalida, KProductoCalificadoEntrada,
)
from app.schemas.k_comun_schemas import KEliminacionSalida
from app.services.k_validaciones import k_obtener_o_404, k_validar_sin_repetidos


class KCalificacionService:
    """RF12: calificaciones, validando que el pedido, el cliente y los productos existan."""

    def __init__(self, k_db: Database):
        self.k_repo = KCalificacionRepository(k_db)
        self.k_repo_pedido = KRepositorioBase(k_db, "pedidos", "id_pedido")
        self.k_repo_producto = KRepositorioBase(k_db, "productos", "id_producto")

    def k_listar(self) -> list[dict]:
        return self.k_repo.k_listar()

    def k_obtener(self, k_id: str) -> dict:
        k_calificacion = self.k_repo.k_obtener(k_id)
        if k_calificacion is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, f"Calificación con id {k_id} no encontrada")
        return k_calificacion

    def k_productos_calificados(self, k_pedido: dict, k_items: list[KProductoCalificadoEntrada]) -> list[dict]:
        k_validar_sin_repetidos([k_item.id_producto for k_item in k_items], "productos")
        k_del_pedido = {k_det["id_producto"] for k_det in k_pedido["detalle"]}
        k_productos = []
        for k_item in k_items:
            if k_item.id_producto not in k_del_pedido:
                raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                    f"El producto {k_item.id_producto} no hace parte del pedido {k_pedido['id_pedido']}")
            k_producto = self.k_repo_producto.k_obtener(k_item.id_producto)
            k_productos.append({"id_producto": k_item.id_producto, "nombre": k_producto["nombre"],
                                "calificacion": k_item.calificacion})
        return k_productos

    def k_crear(self, k_datos: KCalificacionCrear) -> dict:
        k_pedido = k_obtener_o_404(self.k_repo_pedido, k_datos.id_pedido, "Pedido")
        if k_pedido["id_cliente"] != k_datos.id_cliente:
            raise HTTPException(status.HTTP_400_BAD_REQUEST,
                                f"El pedido {k_pedido['id_pedido']} no pertenece al cliente {k_datos.id_cliente}")
        if k_pedido["estado"] != KEstadoPedido.ENTREGADO:
            raise HTTPException(status.HTTP_409_CONFLICT, "Solo se pueden calificar pedidos ENTREGADOS")
        if self.k_repo.k_buscar_por_pedido(k_pedido["id_pedido"]):
            raise HTTPException(status.HTTP_409_CONFLICT, "El pedido ya tiene una calificación registrada")
        k_documento = {
            "id_pedido": k_pedido["id_pedido"],
            "id_cliente": k_pedido["id_cliente"],
            "fecha": k_ahora().isoformat(),
            "calificacion_servicio": k_datos.calificacion_servicio,
            "comentario": k_datos.comentario,
            "productos": self.k_productos_calificados(k_pedido, k_datos.productos),
        }
        return self.k_repo.k_crear(k_documento)

    def k_actualizar(self, k_id: str, k_datos: KCalificacionActualizar) -> dict:
        k_calificacion = self.k_obtener(k_id)
        k_cambios = k_datos.model_dump(exclude_unset=True, exclude={"productos"})
        if k_datos.productos is not None:
            k_pedido = self.k_repo_pedido.k_obtener(k_calificacion["id_pedido"])
            k_cambios["productos"] = self.k_productos_calificados(k_pedido, k_datos.productos)
        if not k_cambios:
            return k_calificacion
        return self.k_repo.k_actualizar(k_id, k_cambios)

    def k_eliminar(self, k_id: str) -> KEliminacionSalida:
        self.k_obtener(k_id)
        self.k_repo.k_eliminar(k_id)
        return KEliminacionSalida(mensaje="Calificación eliminada")

    def k_de_producto(self, k_id_producto: int) -> KCalificacionesProductoSalida:
        k_producto = k_obtener_o_404(self.k_repo_producto, k_id_producto, "Producto")
        k_resultado = self.k_repo.k_calificaciones_de_producto(k_id_producto)
        if k_resultado is None:
            return KCalificacionesProductoSalida(id_producto=k_id_producto, nombre=k_producto["nombre"], promedio=0,
                                                 total_calificaciones=0, calificaciones=[])
        return KCalificacionesProductoSalida(
            id_producto=k_id_producto, nombre=k_producto["nombre"], promedio=round(k_resultado["promedio"], 2),
            total_calificaciones=k_resultado["total_calificaciones"], calificaciones=k_resultado["calificaciones"],
        )
