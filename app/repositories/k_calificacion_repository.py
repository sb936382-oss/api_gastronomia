from typing import Any

from bson import ObjectId
from pymongo import DESCENDING, ReturnDocument
from pymongo.database import Database


def k_documento_a_dict(k_documento: dict) -> dict:
    k_documento["id"] = str(k_documento.pop("_id"))
    return k_documento


class KCalificacionRepository:
    """Consultas a la colección calificaciones de MongoDB (usa el _id ObjectId como identificador)."""

    def __init__(self, k_db: Database):
        self.k_coleccion = k_db["calificaciones"]

    def k_listar(self) -> list[dict]:
        return [k_documento_a_dict(k_doc) for k_doc in self.k_coleccion.find().sort("fecha", DESCENDING)]

    def k_obtener(self, k_id: str) -> dict | None:
        if not ObjectId.is_valid(k_id):
            return None
        k_doc = self.k_coleccion.find_one({"_id": ObjectId(k_id)})
        return k_documento_a_dict(k_doc) if k_doc else None

    def k_buscar_por_pedido(self, k_id_pedido: int) -> dict | None:
        return self.k_coleccion.find_one({"id_pedido": k_id_pedido})

    def k_crear(self, k_documento: dict[str, Any]) -> dict:
        k_resultado = self.k_coleccion.insert_one(k_documento)
        return self.k_obtener(str(k_resultado.inserted_id))

    def k_actualizar(self, k_id: str, k_campos: dict[str, Any]) -> dict:
        k_doc = self.k_coleccion.find_one_and_update({"_id": ObjectId(k_id)}, {"$set": k_campos},
                                                     return_document=ReturnDocument.AFTER)
        return k_documento_a_dict(k_doc)

    def k_eliminar(self, k_id: str) -> None:
        self.k_coleccion.delete_one({"_id": ObjectId(k_id)})

    def k_calificaciones_de_producto(self, k_id_producto: int) -> dict | None:
        """Calificaciones y promedio de un producto con el framework de agregación de MongoDB."""
        k_pipeline = [
            {"$match": {"productos.id_producto": k_id_producto}},
            {"$unwind": "$productos"},
            {"$match": {"productos.id_producto": k_id_producto}},
            {"$sort": {"fecha": -1}},
            {"$group": {
                "_id": "$productos.id_producto",
                "nombre": {"$first": "$productos.nombre"},
                "promedio": {"$avg": "$productos.calificacion"},
                "total_calificaciones": {"$sum": 1},
                "calificaciones": {"$push": {
                    "id": {"$toString": "$_id"},
                    "id_pedido": "$id_pedido",
                    "id_cliente": "$id_cliente",
                    "fecha": "$fecha",
                    "calificacion": "$productos.calificacion",
                    "comentario": "$comentario",
                }},
            }},
        ]
        k_resultado = list(self.k_coleccion.aggregate(k_pipeline))
        return k_resultado[0] if k_resultado else None
