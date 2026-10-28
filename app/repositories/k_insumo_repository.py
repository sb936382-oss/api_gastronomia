from datetime import date, datetime, timedelta
from decimal import Decimal

from pymongo.database import Database

from app.models.k_enums import KEstado
from app.repositories.k_base_repository import K_SIN_ID_MONGO, KRepositorioBase


class KInsumoRepository(KRepositorioBase):
    def __init__(self, k_db: Database):
        super().__init__(k_db, "insumos", "id_insumo")

    def k_convertir(self, k_documento: dict) -> dict:
        # fecha_vencimiento se guarda como datetime a las 00:00; la API la maneja como date
        if isinstance(k_documento.get("fecha_vencimiento"), datetime):
            k_documento["fecha_vencimiento"] = k_documento["fecha_vencimiento"].date()
        return k_documento

    def k_buscar(self, k_filtro: dict, k_orden: str) -> list[dict]:
        return [self.k_convertir(k_doc) for k_doc in self.k_coleccion.find(k_filtro, K_SIN_ID_MONGO).sort(k_orden)]

    def k_stock_bajo(self) -> list[dict]:
        return self.k_buscar({"estado": KEstado.ACTIVO, "$expr": {"$lte": ["$stock_actual", "$stock_minimo"]}},
                             "nombre")

    def k_por_vencer(self, k_hoy: date, k_dias: int) -> list[dict]:
        return self.k_buscar({"estado": KEstado.ACTIVO,
                              "fecha_vencimiento": {"$gte": k_hoy, "$lte": k_hoy + timedelta(days=k_dias)}},
                             "fecha_vencimiento")

    def k_obtener_varios(self, k_ids: list[int]) -> dict[int, dict]:
        return {k_doc["id_insumo"]: k_doc for k_doc in self.k_buscar({"id_insumo": {"$in": k_ids}}, "id_insumo")}

    def k_mover_stock(self, k_id: int, k_cantidad: Decimal, k_costo_unitario: Decimal | None = None) -> None:
        """Suma (o resta si es negativa) la cantidad al stock_actual con $inc y, si se envía, cambia el costo."""
        k_cambios: dict = {"$inc": {"stock_actual": k_cantidad}}
        if k_costo_unitario is not None:
            k_cambios["$set"] = {"costo_unitario": k_costo_unitario}
        self.k_coleccion.update_one({"id_insumo": k_id}, k_cambios)
