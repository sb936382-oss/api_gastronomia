from pymongo.database import Database

from app.repositories.k_base_repository import KRepositorioBase


class KProductoRepository(KRepositorioBase):
    def __init__(self, k_db: Database):
        super().__init__(k_db, "productos", "id_producto")

    def k_obtener_receta(self, k_id_producto: int) -> list[dict]:
        """Insumos (con su costo) que componen la receta de un producto: $lookup une recetas con insumos."""
        k_pipeline = [
            {"$match": {"id_producto": k_id_producto}},
            {"$sort": {"id_receta": 1}},
            {"$lookup": {"from": "insumos", "localField": "id_insumo", "foreignField": "id_insumo", "as": "insumo"}},
            {"$unwind": "$insumo"},
            {"$project": {"_id": 0, "insumo._id": 0}},
        ]
        return list(self.k_db["recetas"].aggregate(k_pipeline))

    def k_obtener_recetas_de(self, k_ids_productos: list[int]) -> list[dict]:
        return list(self.k_db["recetas"].find({"id_producto": {"$in": k_ids_productos}}, {"_id": 0}))
