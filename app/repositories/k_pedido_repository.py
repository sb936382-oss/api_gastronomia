from datetime import datetime
from decimal import Decimal

from pymongo.database import Database

from app.models.k_enums import KEstadoPedido
from app.repositories.k_base_repository import KRepositorioBase


class KPedidoRepository(KRepositorioBase):
    def __init__(self, k_db: Database):
        super().__init__(k_db, "pedidos", "id_pedido")

    def k_resumen_ventas(self, k_desde: datetime, k_hasta: datetime) -> tuple[int, Decimal]:
        """Número de pedidos y total vendido (solo pedidos ENTREGADOS) en el rango de fechas."""
        k_pipeline = [
            {"$match": {"estado": KEstadoPedido.ENTREGADO, "fecha_pedido": {"$gte": k_desde, "$lt": k_hasta}}},
            {"$group": {"_id": None, "numero": {"$sum": 1}, "total": {"$sum": "$total"}}},
        ]
        k_resultado = list(self.k_coleccion.aggregate(k_pipeline))
        if not k_resultado:
            return 0, Decimal("0")
        return k_resultado[0]["numero"], k_resultado[0]["total"]

    def k_productos_mas_vendidos(self, k_limite: int) -> list[dict]:
        k_pipeline = [
            {"$match": {"estado": KEstadoPedido.ENTREGADO}},
            {"$unwind": "$detalle"},
            {"$group": {"_id": "$detalle.id_producto",
                        "cantidad_vendida": {"$sum": "$detalle.cantidad"},
                        "total_vendido": {"$sum": "$detalle.subtotal"}}},
            {"$sort": {"cantidad_vendida": -1, "_id": 1}},
            {"$limit": k_limite},
            {"$lookup": {"from": "productos", "localField": "_id", "foreignField": "id_producto", "as": "producto"}},
            {"$unwind": "$producto"},
            {"$project": {"_id": 0, "id_producto": "$_id", "codigo": "$producto.codigo",
                          "nombre": "$producto.nombre", "cantidad_vendida": 1, "total_vendido": 1}},
        ]
        return list(self.k_coleccion.aggregate(k_pipeline))
