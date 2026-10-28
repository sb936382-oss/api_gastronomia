from typing import Any

from pymongo.database import Database

from app.database.k_conexion_mongo import k_siguiente_id

# No se devuelve el _id (ObjectId) de MongoDB: cada documento tiene su propio id entero (id_producto, id_cliente...)
K_SIN_ID_MONGO = {"_id": 0}


class KRepositorioBase:
    """Consultas CRUD comunes a todas las colecciones de MongoDB."""

    def __init__(self, k_db: Database, k_coleccion: str, k_llave: str):
        self.k_db = k_db
        self.k_nombre = k_coleccion
        self.k_coleccion = k_db[k_coleccion]
        self.k_llave = k_llave

    def k_convertir(self, k_documento: dict) -> dict:
        """Ajusta el documento leído de MongoDB antes de devolverlo (las subclases lo pueden sobrescribir)."""
        return k_documento

    def k_listar(self, **k_filtros: Any) -> list[dict]:
        k_cursor = self.k_coleccion.find(k_filtros, K_SIN_ID_MONGO).sort(self.k_llave)
        return [self.k_convertir(k_doc) for k_doc in k_cursor]

    def k_obtener(self, k_id: int) -> dict | None:
        return self.k_buscar_por(**{self.k_llave: k_id})

    def k_buscar_por(self, **k_filtros: Any) -> dict | None:
        k_doc = self.k_coleccion.find_one(k_filtros, K_SIN_ID_MONGO)
        return self.k_convertir(k_doc) if k_doc else None

    def k_id_de(self, k_documento: dict) -> int:
        return k_documento[self.k_llave]

    def k_tiene_registros(self, k_coleccion_relacionada: str, k_filtro: dict) -> bool:
        """Indica si existen documentos asociados (movimientos) en otra colección. Usado en RN04."""
        return self.k_db[k_coleccion_relacionada].count_documents(k_filtro, limit=1) > 0

    def k_crear(self, k_documento: dict[str, Any]) -> dict:
        k_documento[self.k_llave] = k_siguiente_id(self.k_db, self.k_nombre)
        self.k_coleccion.insert_one(k_documento)
        return self.k_obtener(k_documento[self.k_llave])

    def k_actualizar(self, k_documento: dict, k_datos: dict[str, Any]) -> dict:
        k_id = self.k_id_de(k_documento)
        if k_datos:
            self.k_coleccion.update_one({self.k_llave: k_id}, {"$set": k_datos})
        return self.k_obtener(k_id)

    def k_eliminar(self, k_documento: dict) -> None:
        self.k_coleccion.delete_one({self.k_llave: self.k_id_de(k_documento)})
